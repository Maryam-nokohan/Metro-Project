from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

from utils.loader import build_graph_from_files, apply_capacities_from_file

from algorithms.bfs import bfs_shortest_path
from algorithms.dfs import dfs_path
from algorithms.dijkstra import dijkstra_shortest_path

from algorithms.kruskal import kruskal
from algorithms.prim import prim

from algorithms.dag_shortest_path import (
    topological_sort,
    dag_shortest_path_to_target,
)

from algorithms.bellman_ford import bellman_ford

from algorithms.floyd_warshall import (
    floyd_warshall,
    reconstruct_path as fw_reconstruct_path,
    has_negative_cycle,
)

from algorithms.max_flow import max_flow

from algorithms.articulation import (
    find_articulation_points_and_bridges,
)

from algorithms.dominating_set import greedy_dominating_set

from algorithms.levenshtein import find_closest_station

from algorithms.bidirectional_dijkstra import (
    compare_expanded_nodes,
)


app = FastAPI(title="Qom Metro Router API")

templates = Jinja2Templates(directory="templates")


graph = build_graph_from_files(
    "data/stations.txt",
    "data/edges.txt",
)

apply_capacities_from_file(
    graph,
    "data/capacity.txt",
)


class PathRequest(BaseModel):
    start: str
    goal: str
    criterion: Optional[str] = "distance"


class StationRequest(BaseModel):
    station: str
    criterion: Optional[str] = "distance"


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/api/stations")
def get_stations():
    return {"stations": graph.station_ids()}


@app.post("/api/reachability")
def check_reachability(req: PathRequest):

    bfs_path = bfs_shortest_path(
        graph,
        req.start,
        req.goal,
    )

    dfs_path_result = dfs_path(
        graph,
        req.start,
        req.goal,
    )

    return {
        "bfs_path": bfs_path,
        "dfs_path": dfs_path_result,
    }


@app.post("/api/shortest-path")
def shortest_path(req: PathRequest):

    path, cost = dijkstra_shortest_path(
        graph,
        req.start,
        req.goal,
        req.criterion,
    )

    return {
        "path": path,
        "cost": cost,
        "criterion": req.criterion,
    }


@app.get("/api/mst")
def get_mst(
    criterion: str = "distance",
):

    kruskal_result = kruskal(
        graph,
        criterion,
    )

    prim_result = prim(
        graph,
        criterion=criterion,
    )

    return {
        "criterion": criterion,
        "kruskal_cost": kruskal_result.total_cost,
        "prim_cost": prim_result.total_cost,
        "edges": [
            {
                "source": edge.source,
                "destination": edge.destination,
                "weight": edge.get_weight(criterion),
            }
            for edge in kruskal_result.edges
        ],
    }


@app.get("/api/dag")
def get_dag():

    order = topological_sort(graph)

    if order is None:
        return {
            "is_dag": False,
            "topological_order": None,
        }

    return {
        "is_dag": True,
        "topological_order": order,
    }


@app.post("/api/dag-shortest-path")
def dag_shortest_path(req: PathRequest):

    try:
        path, cost = dag_shortest_path_to_target(
            graph,
            req.start,
            req.goal,
            req.criterion,
        )

        return {
            "is_dag": True,
            "path": path,
            "cost": cost,
            "criterion": req.criterion,
        }

    except ValueError as error:
        return {
            "is_dag": False,
            "path": None,
            "cost": None,
            "error": str(error),
        }


@app.post("/api/bellman-ford")
def bellman_ford_route(req: StationRequest):

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
def get_floyd_warshall(
    criterion: str = "distance",
):

    station_ids, distances, next_hop = floyd_warshall(
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
        "cost": cost,
        "criterion": req.criterion,
    }


@app.get("/api/critical-nodes")
def critical_nodes():

    points, bridges = find_articulation_points_and_bridges(graph)

    return {
        "points": list(points),
        "bridges": bridges,
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

    results = find_closest_station(
        q,
        graph.station_ids(),
        max_results=3,
    )

    return {
        "query": q,
        "results": [
            {
                "name": result[0],
                "distance": result[1],
            }
            for result in results
        ],
    }


@app.post("/api/compare-routing")
def compare_routing(req: PathRequest):

    result = compare_expanded_nodes(
        graph,
        req.start,
        req.goal,
        req.criterion,
    )

    return result
