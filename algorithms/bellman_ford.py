# algorithms/bellman_ford.py

from typing import Dict, List, Optional, Tuple

from models.graph import Graph


def _reconstruct_negative_cycle(
    parent: Dict[str, str],
    start: str,
    vertex_count: int,
) -> Optional[List[str]]:
    """
    Reconstruct a reachable negative cycle from a vertex
    whose distance can still be relaxed after V-1 rounds.
    """

    current = start

    for _ in range(vertex_count):
        if current not in parent:
            return None

        current = parent[current]

    cycle = [current]
    node = parent.get(current)

    while node is not None and node != current:
        cycle.append(node)

        if len(cycle) > vertex_count + 1:
            return None

        node = parent.get(node)

    if node != current:
        return None

    cycle.append(current)
    cycle.reverse()

    return cycle


def bellman_ford(
    graph: Graph,
    start: str,
    criterion: str = "weight",
) -> Tuple[
    Dict[str, float],
    Dict[str, str],
    List[str],
]:
    """
    T2.4 - Bellman-Ford.

    Returns:
        distances
        parent map
        one reachable negative cycle, if it exists
    """

    if not graph.has_station(start):
        return {}, {}, []

    dist = {
        station_id: float("inf")
        for station_id in graph.station_ids()
    }

    parent: Dict[str, str] = {}

    dist[start] = 0.0

    vertices = graph.station_ids()
    vertex_count = len(vertices)

    for _ in range(max(0, vertex_count - 1)):
        updated = False

        for u in vertices:
            if dist[u] == float("inf"):
                continue

            for edge in graph.neighbors(u):
                v = edge.destination
                weight = edge.get_weight(criterion)

                candidate = dist[u] + weight

                if candidate < dist[v]:
                    dist[v] = candidate
                    parent[v] = u
                    updated = True

        if not updated:
            break

    cycle_vertex: Optional[str] = None

    for u in vertices:
        if dist[u] == float("inf"):
            continue

        for edge in graph.neighbors(u):
            v = edge.destination
            weight = edge.get_weight(criterion)

            if dist[u] + weight < dist[v]:
                parent[v] = u
                cycle_vertex = v
                break

        if cycle_vertex is not None:
            break

    negative_cycle: List[str] = []

    if cycle_vertex is not None:
        reconstructed = _reconstruct_negative_cycle(
            parent,
            cycle_vertex,
            vertex_count,
        )

        if reconstructed:
            negative_cycle = reconstructed

    return dist, parent, negative_cycle