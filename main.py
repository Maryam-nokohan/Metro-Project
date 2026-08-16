from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional

from utils.loader import build_graph_from_files, apply_capacities_from_file
from algorithms.bfs import bfs_shortest_path
from algorithms.dfs import dfs_path
from algorithms.dijkstra import dijkstra_shortest_path
from algorithms.kruskal import kruskal
from algorithms.prim import prim
from algorithms.bellman_ford import bellman_ford
from algorithms.floyd_warshall import floyd_warshall, reconstruct_path as fw_reconstruct_path
from algorithms.max_flow import max_flow
from algorithms.articulation import find_articulation_points_and_bridges
from algorithms.dominating_set import greedy_dominating_set
from algorithms.levenshtein import find_closest_station

app = FastAPI(title="Qom Metro Router API")
templates = Jinja2Templates(directory="templates")

# Load graph data on startup
graph = build_graph_from_files("data/stations.txt", "data/edges.txt")
apply_capacities_from_file(graph, "data/capacity.txt")

class PathRequest(BaseModel):
    start: str
    goal: str
    criterion: Optional[str] = "distance"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/stations")
def get_stations():
    return {"stations": graph.station_ids()}

@app.post("/api/reachability")
def check_reachability(req: PathRequest):
    bfs_p = bfs_shortest_path(graph, req.start, req.goal)
    dfs_p = dfs_path(graph, req.start, req.goal)
    return {"bfs_path": bfs_p, "dfs_path": dfs_p}

@app.post("/api/shortest-path")
def shortest_path(req: PathRequest):
    path, cost = dijkstra_shortest_path(graph, req.start, req.goal, req.criterion)
    return {"path": path, "cost": cost}

@app.get("/api/mst")
def get_mst(criterion: str = "distance"):
    k_res = kruskal(graph, criterion)
    p_res = prim(graph, criterion=criterion)
    return {
        "kruskal_cost": k_res.total_cost,
        "prim_cost": p_res.total_cost,
        "edges": [{"source": e.source, "destination": e.destination, "weight": e.get_weight(criterion)} for e in k_res.edges]
    }

@app.get("/api/critical-nodes")
def critical_nodes():
    points, bridges = find_articulation_points_and_bridges(graph)
    return {"points": list(points), "bridges": bridges}

@app.get("/api/dominating-set")
def dominating_set():
    solution = greedy_dominating_set(graph)
    return {"solution": solution}

@app.get("/api/search")
def search_station(q: str):
    results = find_closest_station(q, graph.station_ids(), max_results=3)
    return {"results": [{"name": r[0], "distance": r[1]} for r in results]}
