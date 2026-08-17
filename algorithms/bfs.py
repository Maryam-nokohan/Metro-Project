from collections import deque
from typing import Dict, List, Optional

from models.graph import Graph


def bfs_traversal(graph: Graph, start_id: str) -> List[str]:

    if not graph.has_station(start_id):
        return []

    visited = {start_id}
    order: List[str] = []
    queue = deque([start_id])

    while queue:
        current = queue.popleft()
        order.append(current)
        for edge in graph.neighbors(current):
            if edge.destination not in visited:
                visited.add(edge.destination)
                queue.append(edge.destination)

    return order


def bfs_shortest_path(graph: Graph, start_id: str, goal_id: str) -> Optional[List[str]]:

    if not graph.has_station(start_id) or not graph.has_station(goal_id):
        return None

    if start_id == goal_id:
        return [start_id]

    visited = {start_id}
    parent: Dict[str, str] = {}
    queue = deque([start_id])

    while queue:
        current = queue.popleft()
        for edge in graph.neighbors(current):
            neighbor = edge.destination
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parent[neighbor] = current

            if neighbor == goal_id:
                path = [goal_id]
                while path[-1] != start_id:
                    path.append(parent[path[-1]])
                path.reverse()
                return path

            queue.append(neighbor)

    return None


def is_reachable_bfs(graph: Graph, start_id: str, goal_id: str) -> bool:

    return bfs_shortest_path(graph, start_id, goal_id) is not None
