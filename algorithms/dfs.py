from typing import Dict, List, Optional, Set

from models.graph import Graph


def dfs_traversal(graph: Graph, start_id: str) -> List[str]:

    if not graph.has_station(start_id):
        return []

    visited: Set[str] = set()
    order: List[str] = []
    stack = [start_id]

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        order.append(current)
        for edge in reversed(graph.neighbors(current)):
            if edge.destination not in visited:
                stack.append(edge.destination)

    return order


def dfs_path(graph: Graph, start_id: str, goal_id: str) -> Optional[List[str]]:

    if not graph.has_station(start_id) or not graph.has_station(goal_id):
        return None

    if start_id == goal_id:
        return [start_id]

    visited: Set[str] = {start_id}
    parent: Dict[str, str] = {}
    stack = [start_id]

    while stack:
        current = stack.pop()
        if current == goal_id:
            path = [goal_id]
            while path[-1] != start_id:
                path.append(parent[path[-1]])
            path.reverse()
            return path

        for edge in graph.neighbors(current):
            neighbor = edge.destination
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)

    return None


def is_reachable_dfs(graph: Graph, start_id: str, goal_id: str) -> bool:

    return dfs_path(graph, start_id, goal_id) is not None