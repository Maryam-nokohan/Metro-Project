from collections import deque
from typing import Dict, List, Optional, Tuple

from models.graph import Graph


def topological_sort(graph: Graph) -> Optional[List[str]]:
    """
    Kahn Algorithm
    Returns:
        topological order
        None if graph contains cycle
    """

    indegree = {station: 0 for station in graph.station_ids()}

    for station in graph.station_ids():
        for edge in graph.neighbors(station):
            indegree[edge.destination] += 1

    queue = deque()

    for node, deg in indegree.items():
        if deg == 0:
            queue.append(node)

    order = []

    while queue:
        current = queue.popleft()

        order.append(current)

        for edge in graph.neighbors(current):
            neighbor = edge.destination

            indegree[neighbor] -= 1

            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != graph.num_stations():
        return None

    return order


def dag_shortest_path(
    graph: Graph,
    start: str,
    criterion: str = "distance",
) -> Tuple[Dict[str, float], Dict[str, str]]:

    order = topological_sort(graph)

    if order is None:
        raise ValueError("Graph is not DAG")

    dist = {station: float("inf") for station in graph.station_ids()}

    parent = {}

    dist[start] = 0

    for node in order:
        if dist[node] == float("inf"):
            continue

        for edge in graph.neighbors(node):
            weight = edge.get_weight(criterion)

            new_dist = dist[node] + weight

            if new_dist < dist[edge.destination]:
                dist[edge.destination] = new_dist

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

    while path[-1] != start:
        path.append(parent[path[-1]])

    path.reverse()

    return path


def dag_shortest_path_to_target(
    graph: Graph,
    start: str,
    goal: str,
    criterion: str = "distance",
):

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
