from __future__ import annotations

import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from algorithms.articulation import find_articulation_points_and_bridges
from algorithms.bellman_ford import bellman_ford
from algorithms.bidirectional_dijkstra import compare_expanded_nodes
from algorithms.bfs import bfs_shortest_path
from algorithms.dag_shortest_path import (
    dag_shortest_path_to_target,
    topological_sort,
)
from algorithms.dfs import dfs_path
from algorithms.dijkstra import dijkstra_shortest_path
from algorithms.dominating_set import greedy_dominating_set
from algorithms.floyd_warshall import (
    floyd_warshall,
    has_negative_cycle,
    reconstruct_path as fw_reconstruct_path,
)
from algorithms.interval_scheduling import select_max_trains
from algorithms.kruskal import kruskal
from algorithms.levenshtein import find_closest_station
from algorithms.max_flow import max_flow
from algorithms.prim import prim
from models.graph import Graph
from models.train import Train, TrainDispatchQueue
from simulation.passenger_simulator import GateSimulator
from utils.analytics import OperationsLog
from utils.loader import apply_capacities_from_file, build_graph_from_files

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

STATIONS_PATH = os.path.join(DATA_DIR, "stations.txt")
EDGES_PATH = os.path.join(DATA_DIR, "edges.txt")
CAPACITY_PATH = os.path.join(DATA_DIR, "capacity.txt")


app = FastAPI(
    title="Qom Metro Management System",
    version="2.0.0",
)

templates = Jinja2Templates(directory=TEMPLATES_DIR)

graph = build_graph_from_files(
    STATIONS_PATH,
    EDGES_PATH,
)

if os.path.exists(CAPACITY_PATH):
    apply_capacities_from_file(graph, CAPACITY_PATH)


DEFAULT_EXPRESS_LINE = [
    "ایستگاه ترمینال مسافربری قم",
    "ایستگاه قلعه کامکار",
    "ایستگاه میدان کشاورز",
    "ایستگاه میدان مطهری",
    "ایستگاه بیمارستان نکویی",
    "ایستگاه میدان بقیه الله",
    "ایستگاه مسجد مقدس جمکران",
]


def build_express_graph(
    base_graph: Graph,
    stations: List[str],
) -> Graph:
    if len(stations) < 2:
        raise ValueError("خط Express باید حداقل دو ایستگاه داشته باشد.")

    if len(set(stations)) != len(stations):
        raise ValueError("یک ایستگاه نمی‌تواند بیش از یک بار در خط Express باشد.")

    express = Graph(directed=True)

    for station_id in stations:
        if not base_graph.has_station(station_id):
            raise ValueError(f"ایستگاه وجود ندارد: {station_id}")
        express.add_station(base_graph.get_station(station_id))

    for source, destination in zip(stations, stations[1:]):
        edge = base_graph.get_edge(source, destination)

        if edge is None:
            raise ValueError(
                f"مسیر مستقیم بین «{source}» و «{destination}» در شبکه اصلی وجود ندارد."
            )

        express.add_edge(
            source_id=source,
            destination_id=destination,
            distance=edge.distance,
            time=edge.time,
            weight=edge.weight,
            capacity=edge.capacity,
            directed=True,
        )

    return express


express_graph = build_express_graph(
    graph,
    DEFAULT_EXPRESS_LINE,
)


dispatch_queue = TrainDispatchQueue()
operations_log = OperationsLog()


class PathRequest(BaseModel):
    start: str
    goal: str
    criterion: str = "distance"


class StationRequest(BaseModel):
    station: str
    criterion: str = "weight"


class ExpressPathRequest(BaseModel):
    start: str
    goal: str
    criterion: str = "distance"


class ExpressLineRequest(BaseModel):
    stations: List[str] = Field(min_length=2)


class TrainInput(BaseModel):
    train_id: str
    arrival_time: float
    departure_time: float
    delay_minutes: float = 0.0
    is_emergency: bool = False


class TrainScheduleRequest(BaseModel):
    trains: List[TrainInput]


class DispatchTrainRequest(BaseModel):
    train: TrainInput


class RemoveTrainRequest(BaseModel):
    train_id: str


class TripRecordRequest(BaseModel):
    date: str
    station_id: str
    count: int = Field(default=1, ge=1)


class BusiestStationRequest(BaseModel):
    k: int = Field(ge=1)


class PassengerSimulationRequest(BaseModel):
    num_gates: int = Field(default=2, ge=1)
    duration_minutes: float = Field(default=60.0, gt=0)
    avg_arrivals_per_minute: float = Field(default=1.0, gt=0)
    service_time_seconds: float = Field(default=3.0, gt=0)
    seed: Optional[int] = None


def validate_criterion(criterion: str, allow_weight: bool = False) -> None:
    allowed = {"distance", "time"}

    if allow_weight:
        allowed.add("weight")

    if criterion not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"criterion باید یکی از {sorted(allowed)} باشد.",
        )


def train_from_input(data: TrainInput) -> Train:
    if data.arrival_time < 0:
        raise HTTPException(
            status_code=400,
            detail="زمان ورود نمی‌تواند منفی باشد.",
        )

    if data.departure_time < data.arrival_time:
        raise HTTPException(
            status_code=400,
            detail="زمان خروج باید بزرگ‌تر یا مساوی زمان ورود باشد.",
        )

    if data.delay_minutes < 0:
        raise HTTPException(
            status_code=400,
            detail="میزان تأخیر نمی‌تواند منفی باشد.",
        )

    return Train(
        train_id=data.train_id,
        arrival_time=data.arrival_time,
        departure_time=data.departure_time,
        delay_minutes=data.delay_minutes,
        is_emergency=data.is_emergency,
    )


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/api/stations")
def get_stations():
    return {
        "stations": graph.station_ids(),
        "count": graph.num_stations(),
        "edges": graph.num_edges(),
    }


@app.post("/api/reachability")
def check_reachability(req: PathRequest):
    if not graph.has_station(req.start):
        raise HTTPException(404, f"ایستگاه مبدأ وجود ندارد: {req.start}")

    if not graph.has_station(req.goal):
        raise HTTPException(404, f"ایستگاه مقصد وجود ندارد: {req.goal}")

    return {
        "reachable": bfs_shortest_path(
            graph,
            req.start,
            req.goal,
        )
        is not None,
        "bfs_path": bfs_shortest_path(
            graph,
            req.start,
            req.goal,
        ),
        "dfs_path": dfs_path(
            graph,
            req.start,
            req.goal,
        ),
    }


@app.post("/api/shortest-path")
def shortest_path(req: PathRequest):
    validate_criterion(req.criterion)

    path, cost = dijkstra_shortest_path(
        graph,
        req.start,
        req.goal,
        req.criterion,
    )

    return {
        "path": path,
        "cost": None if cost == float("inf") else cost,
        "criterion": req.criterion,
    }


@app.get("/api/mst")
def get_mst(criterion: str = "distance"):
    validate_criterion(criterion)

    kruskal_result = kruskal(
        graph,
        criterion=criterion,
    )

    prim_result = prim(
        graph,
        criterion=criterion,
    )

    return {
        "criterion": criterion,
        "kruskal_cost": kruskal_result.total_cost,
        "prim_cost": prim_result.total_cost,
        "same_cost": (abs(kruskal_result.total_cost - prim_result.total_cost) < 1e-9),
        "kruskal_edges": [
            {
                "source": edge.source,
                "destination": edge.destination,
                "weight": edge.get_weight(criterion),
            }
            for edge in kruskal_result.edges
        ],
        "prim_edges": [
            {
                "source": edge.source,
                "destination": edge.destination,
                "weight": edge.get_weight(criterion),
            }
            for edge in prim_result.edges
        ],
    }


@app.get("/api/dag")
def get_dag():
    order = topological_sort(express_graph)

    return {
        "is_dag": order is not None,
        "express_line": express_graph.station_ids(),
        "edges": [
            {
                "source": edge.source,
                "destination": edge.destination,
                "distance": edge.distance,
                "time": edge.time,
                "weight": edge.weight,
            }
            for edge in express_graph.edges()
        ],
        "topological_order": order,
    }


@app.post("/api/express-line")
def create_express_line(req: ExpressLineRequest):
    global express_graph

    try:
        candidate = build_express_graph(
            graph,
            req.stations,
        )

        order = topological_sort(candidate)

        if order is None:
            raise ValueError("خط Express باید DAG باشد.")

        express_graph = candidate

        return {
            "is_dag": True,
            "express_line": express_graph.station_ids(),
            "topological_order": order,
            "edges": [
                {
                    "source": edge.source,
                    "destination": edge.destination,
                    "distance": edge.distance,
                    "time": edge.time,
                    "weight": edge.weight,
                }
                for edge in express_graph.edges()
            ],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post("/api/dag-shortest-path")
def dag_shortest_path(req: ExpressPathRequest):
    validate_criterion(req.criterion)

    if not express_graph.has_station(req.start):
        raise HTTPException(
            status_code=404,
            detail="مبدأ در خط Express وجود ندارد.",
        )

    if not express_graph.has_station(req.goal):
        raise HTTPException(
            status_code=404,
            detail="مقصد در خط Express وجود ندارد.",
        )

    path, cost = dag_shortest_path_to_target(
        express_graph,
        req.start,
        req.goal,
        req.criterion,
    )

    return {
        "is_dag": True,
        "path": path,
        "cost": None if cost == float("inf") else cost,
        "criterion": req.criterion,
        "express_line": express_graph.station_ids(),
    }


@app.post("/api/bellman-ford")
def bellman_ford_route(req: StationRequest):
    validate_criterion(
        req.criterion,
        allow_weight=True,
    )

    if not graph.has_station(req.station):
        raise HTTPException(
            status_code=404,
            detail=f"ایستگاه وجود ندارد: {req.station}",
        )

    dist, parent, negative_cycle = bellman_ford(
        graph,
        req.station,
        req.criterion,
    )

    return {
        "start": req.station,
        "criterion": req.criterion,
        "distances": {
            station: (None if value == float("inf") else value)
            for station, value in dist.items()
        },
        "negative_cycle": negative_cycle,
        "has_negative_cycle": bool(negative_cycle),
    }


@app.post("/api/max-flow")
def calculate_max_flow(req: PathRequest):
    flow = max_flow(
        graph,
        req.start,
        req.goal,
    )

    return {
        "source": req.start,
        "sink": req.goal,
        "max_flow": flow,
    }


@app.get("/api/floyd-warshall")
def get_floyd_warshall(criterion: str = "distance"):
    validate_criterion(criterion)

    station_ids, distances, _next_hop = floyd_warshall(
        graph,
        criterion,
    )

    return {
        "criterion": criterion,
        "stations": station_ids,
        "distances": [
            [None if value == float("inf") else value for value in row]
            for row in distances
        ],
        "has_negative_cycle": has_negative_cycle(distances),
    }


@app.post("/api/floyd-warshall/path")
def floyd_warshall_path(req: PathRequest):
    validate_criterion(req.criterion)

    station_ids, distances, next_hop = floyd_warshall(
        graph,
        req.criterion,
    )

    path = fw_reconstruct_path(
        station_ids,
        next_hop,
        req.start,
        req.goal,
    )

    if path is None:
        return {
            "path": None,
            "cost": None,
            "criterion": req.criterion,
        }

    index = {station: i for i, station in enumerate(station_ids)}

    cost = distances[index[req.start]][index[req.goal]]

    return {
        "path": path,
        "cost": (None if cost == float("inf") else cost),
        "criterion": req.criterion,
    }


@app.get("/api/critical-nodes")
def critical_nodes():
    points, bridges = find_articulation_points_and_bridges(graph)

    return {
        "points": sorted(points),
        "bridges": [list(bridge) for bridge in bridges],
    }


@app.get("/api/dominating-set")
def dominating_set():
    solution = greedy_dominating_set(graph)

    return {
        "solution": solution,
        "count": len(solution),
    }


@app.get("/api/search")
def search_station(q: str):
    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="عبارت جستجو نمی‌تواند خالی باشد.",
        )

    results = find_closest_station(
        query,
        graph.station_ids(),
        max_results=5,
    )

    return {
        "query": query,
        "results": [
            {
                "name": name,
                "distance": distance,
            }
            for name, distance in results
        ],
    }


@app.post("/api/compare-routing")
def compare_routing(req: PathRequest):
    validate_criterion(req.criterion)

    return compare_expanded_nodes(
        graph,
        req.start,
        req.goal,
        req.criterion,
    )


@app.post("/api/t3/trains/schedule")
def schedule_trains(req: TrainScheduleRequest):
    trains = [train_from_input(train) for train in req.trains]

    selected = select_max_trains(trains)

    return {
        "selected_count": len(selected),
        "selected_trains": [
            {
                "train_id": train.train_id,
                "arrival_time": train.arrival_time,
                "departure_time": train.departure_time,
                "delay_minutes": train.delay_minutes,
                "is_emergency": train.is_emergency,
            }
            for train in selected
        ],
    }


@app.post("/api/t3/dispatch/add")
def add_dispatch_train(req: DispatchTrainRequest):
    train = train_from_input(req.train)

    dispatch_queue.add_train(train)

    next_train = dispatch_queue.peek_next()

    return {
        "added": train.train_id,
        "queue_size": len(dispatch_queue),
        "next_train": (None if next_train is None else next_train.train_id),
    }


@app.delete("/api/t3/dispatch/{train_id}")
def remove_dispatch_train(train_id: str):
    removed = dispatch_queue.remove_train(train_id)

    return {
        "removed": removed,
        "train_id": train_id,
        "queue_size": len(dispatch_queue),
    }


@app.get("/api/t3/dispatch/next")
def peek_dispatch_train():
    train = dispatch_queue.peek_next()

    if train is None:
        return {
            "train": None,
            "queue_size": 0,
        }

    return {
        "train": {
            "train_id": train.train_id,
            "arrival_time": train.arrival_time,
            "departure_time": train.departure_time,
            "delay_minutes": train.delay_minutes,
            "is_emergency": train.is_emergency,
            "priority": train.priority_score(),
        },
        "queue_size": len(dispatch_queue),
    }


@app.post("/api/t3/dispatch/dispatch")
def dispatch_next_train():
    train = dispatch_queue.dispatch_next()

    if train is None:
        return {
            "train": None,
            "queue_size": 0,
        }

    return {
        "train": {
            "train_id": train.train_id,
            "arrival_time": train.arrival_time,
            "departure_time": train.departure_time,
            "delay_minutes": train.delay_minutes,
            "is_emergency": train.is_emergency,
            "priority": train.priority_score(),
        },
        "queue_size": len(dispatch_queue),
    }


@app.post("/api/t3/analytics/trips")
def record_trip(req: TripRecordRequest):
    if not graph.has_station(req.station_id):
        raise HTTPException(
            status_code=404,
            detail=f"ایستگاه وجود ندارد: {req.station_id}",
        )

    operations_log.record_trip(
        date=req.date,
        station_id=req.station_id,
        count=req.count,
    )

    return {
        "success": True,
        "total_records": operations_log.total_records(),
    }


@app.get("/api/t3/analytics/average-daily")
def average_daily_trips():
    return {
        "average_daily_trips": operations_log.average_daily_trips(),
    }


@app.post("/api/t3/analytics/kth-busiest")
def kth_busiest_station(req: BusiestStationRequest):
    result = operations_log.kth_busiest_station(req.k)

    if result is None:
        return {
            "found": False,
            "station": None,
            "trip_count": None,
        }

    station, count = result

    return {
        "found": True,
        "station": station,
        "trip_count": count,
        "k": req.k,
    }


@app.post("/api/t3/simulation")
def simulate_passengers(
    req: PassengerSimulationRequest,
):
    simulator = GateSimulator(
        num_gates=req.num_gates,
        service_time_seconds=req.service_time_seconds,
        seed=req.seed,
    )

    passengers = simulator.generate_arrivals(
        duration_minutes=req.duration_minutes,
        avg_arrivals_per_minute=req.avg_arrivals_per_minute,
    )

    result = simulator.simulate(passengers)

    waiting_times = [
        passenger.waiting_time
        for passenger in result
        if passenger.waiting_time is not None
    ]

    return {
        "passenger_count": len(result),
        "num_gates": req.num_gates,
        "service_time_seconds": req.service_time_seconds,
        "duration_minutes": req.duration_minutes,
        "average_waiting_time_minutes": (GateSimulator.average_waiting_time(result)),
        "max_waiting_time_minutes": (GateSimulator.max_waiting_time(result)),
        "passengers": [
            {
                "passenger_id": passenger.passenger_id,
                "arrival_time": passenger.arrival_time,
                "service_start_time": passenger.service_start_time,
                "service_end_time": passenger.service_end_time,
                "waiting_time": passenger.waiting_time,
            }
            for passenger in result
        ],
    }
