from collections import deque
from typing import Dict, List, Optional, Tuple

from models.graph import Graph


def topological_sort(
    graph: Graph,
) -> Optional[List[str]]:
    """
    Kahn's algorithm.

    A DAG must be directed. An undirected metro graph is
    NOT automatically a DAG.
    """

    if not graph.directed:
        return None

    indegree = {station_id: 0 for station_id in graph.station_ids()}

    for station_id in graph.station_ids():
        for edge in graph.neighbors(station_id):
            indegree[edge.destination] += 1

    queue = deque(station_id for station_id, degree in indegree.items() if degree == 0)

    order: List[str] = []

    while queue:
        current = queue.popleft()
        order.append(current)

        for edge in graph.neighbors(current):
            indegree[edge.destination] -= 1

            if indegree[edge.destination] == 0:
                queue.append(edge.destination)

    if len(order) != graph.num_stations():
        return None

    return order


def dag_shortest_path(
    graph: Graph,
    start: str,
    criterion: str = "distance",
) -> Tuple[Dict[str, float], Dict[str, str]]:
    if not graph.directed:
        raise ValueError("Shortest path by DAG algorithm requires a directed graph.")

    if not graph.has_station(start):
        raise ValueError(f"ایستگاه مبدأ وجود ندارد: {start}")

    order = topological_sort(graph)

    if order is None:
        raise ValueError("گراف دارای دور است و DAG نیست.")

    dist = {station_id: float("inf") for station_id in graph.station_ids()}

    parent: Dict[str, str] = {}

    dist[start] = 0.0

    for node in order:
        if dist[node] == float("inf"):
            continue

        for edge in graph.neighbors(node):
            weight = edge.get_weight(criterion)

            candidate = dist[node] + weight

            if candidate < dist[edge.destination]:
                dist[edge.destination] = candidate
                parent[edge.destination] = node

    return dist, parent


def reconstruct_path(
    parent: Dict[str, str],
    start: str,
    goal: str,
) -> Optional[List[str]]:
    if start == goal:
        return [start]

    if goal not in parent:
        return None

    path = [goal]
    current = goal

    visited = {goal}

    while current != start:
        if current not in parent:
            return None

        current = parent[current]

        if current in visited:
            return None

        visited.add(current)
        path.append(current)

    path.reverse()

    return path


def dag_shortest_path_to_target(
    graph: Graph,
    start: str,
    goal: str,
    criterion: str = "distance",
) -> Tuple[Optional[List[str]], float]:
    if not graph.has_station(start):
        return None, float("inf")

    if not graph.has_station(goal):
        return None, float("inf")

    dist, parent = dag_shortest_path(
        graph,
        start,
        criterion,
    )

    if dist[goal] == float("inf"):
        return None, float("inf")

    path = reconstruct_path(
        parent,
        start,
        goal,
    )

    return path, dist[goal]
