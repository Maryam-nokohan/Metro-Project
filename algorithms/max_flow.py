from collections import deque, defaultdict
from typing import Dict, Optional

from models.graph import Graph


def _build_residual_graph(graph: Graph) -> Dict[str, Dict[str, float]]:

    residual: Dict[str, Dict[str, float]] = defaultdict(dict)

    for station_id in graph.station_ids():
        residual[station_id]

    for edge in graph.edges():
        capacity = edge.capacity if edge.capacity is not None else 0.0

        residual[edge.source][edge.destination] = (
            residual[edge.source].get(edge.destination, 0.0) + capacity
        )
        residual[edge.destination].setdefault(edge.source, 0.0)

        if not edge.directed:
            residual[edge.destination][edge.source] = (
                residual[edge.destination].get(edge.source, 0.0) + capacity
            )
            residual[edge.source].setdefault(edge.destination, 0.0)

    return residual


def _bfs_find_augmenting_path(
    residual: Dict[str, Dict[str, float]], source: str, sink: str
) -> Optional[Dict[str, str]]:

    parent: Dict[str, str] = {}
    visited = {source}
    queue = deque([source])

    while queue:
        u = queue.popleft()
        if u == sink:
            return parent
        for v, cap in residual[u].items():
            if cap > 0 and v not in visited:
                visited.add(v)
                parent[v] = u
                queue.append(v)

    return None


def max_flow(graph: Graph, source_id: str, sink_id: str) -> float:

    if not graph.has_station(source_id) or not graph.has_station(sink_id):
        return 0.0
    if source_id == sink_id:
        return 0.0

    residual = _build_residual_graph(graph)
    total_flow = 0.0

    while True:
        parent = _bfs_find_augmenting_path(residual, source_id, sink_id)
        if parent is None:
            break

        bottleneck = float("inf")
        v = sink_id
        while v != source_id:
            u = parent[v]
            bottleneck = min(bottleneck, residual[u][v])
            v = u

        v = sink_id
        while v != source_id:
            u = parent[v]
            residual[u][v] -= bottleneck
            residual[v][u] += bottleneck
            v = u

        total_flow += bottleneck

    return total_flow
