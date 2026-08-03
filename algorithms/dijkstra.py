import heapq
from typing import Dict, List, Optional, Tuple

from models.graph import Graph


VALID_CRITERIA = ("distance", "time")


def dijkstra(
    graph: Graph, start_id: str, criterion: str = "distance"
) -> Tuple[Dict[str, float], Dict[str, str]]:

    if criterion not in VALID_CRITERIA:
        raise ValueError(
            f"معیار نامعتبر: {criterion!r} (باید 'distance' یا 'time' باشد)"
        )

    if not graph.has_station(start_id):
        return {}, {}

    dist: Dict[str, float] = {start_id: 0.0}
    parent: Dict[str, str] = {}
    visited = set()

    heap: List[Tuple[float, str]] = [(0.0, start_id)]

    while heap:
        current_dist, current_id = heapq.heappop(heap)

        if current_id in visited:
            continue
        visited.add(current_id)

        for edge in graph.neighbors(current_id):
            weight = edge.get_weight(criterion)
            if weight < 0:
                raise ValueError(
                    "Dijkstra با وزن منفی کار نمی‌کند؛ برای گراف‌هایی با "
                    "وزن منفی از algorithms/bellman_ford.py (تسک T2.4) استفاده کنید."
                )

            neighbor_id = edge.destination
            new_dist = current_dist + weight

            if neighbor_id not in dist or new_dist < dist[neighbor_id]:
                dist[neighbor_id] = new_dist
                parent[neighbor_id] = current_id
                heapq.heappush(heap, (new_dist, neighbor_id))

    return dist, parent


def reconstruct_path(
    parent: Dict[str, str], start_id: str, goal_id: str
) -> Optional[List[str]]:

    if goal_id == start_id:
        return [start_id]
    if goal_id not in parent:
        return None

    path = [goal_id]
    while path[-1] != start_id:
        path.append(parent[path[-1]])
    path.reverse()
    return path


def dijkstra_shortest_path(
    graph: Graph, start_id: str, goal_id: str, criterion: str = "distance"
) -> Tuple[Optional[List[str]], float]:

    if not graph.has_station(start_id) or not graph.has_station(goal_id):
        return None, float("inf")

    dist, parent = dijkstra(graph, start_id, criterion)

    if goal_id not in dist:
        return None, float("inf") 

    path = reconstruct_path(parent, start_id, goal_id)
    return path, dist[goal_id]