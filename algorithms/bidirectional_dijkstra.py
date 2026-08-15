import heapq
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from models.graph import Graph


def _build_reverse_adjacency(graph: Graph) -> Dict[str, list]:

    reverse: Dict[str, list] = defaultdict(list)
    for station_id in graph.station_ids():
        reverse[station_id] 

    for edge in graph.edges():
        reverse[edge.destination].append(edge)
        if not edge.directed:
            reverse[edge.source].append(edge.reversed())

    return reverse


def bidirectional_dijkstra(
    graph: Graph, source_id: str, target_id: str, criterion: str = "distance"
) -> Tuple[Optional[List[str]], float, int]:
  
    if not graph.has_station(source_id) or not graph.has_station(target_id):
        return None, float("inf"), 0

    if source_id == target_id:
        return [source_id], 0.0, 0

    reverse_adjacency = _build_reverse_adjacency(graph)

    dist_f: Dict[str, float] = {source_id: 0.0}
    dist_b: Dict[str, float] = {target_id: 0.0}
    parent_f: Dict[str, str] = {}
    parent_b: Dict[str, str] = {}
    visited_f = set()
    visited_b = set()
    pq_f: List[Tuple[float, str]] = [(0.0, source_id)]
    pq_b: List[Tuple[float, str]] = [(0.0, target_id)]

    best = float("inf")
    meeting_node: Optional[str] = None
    expanded_nodes = 0

    def _relax_forward(u: str) -> None:
        nonlocal best, meeting_node
        for edge in graph.neighbors(u):
            v = edge.destination
            weight = edge.get_weight(criterion)
            new_dist = dist_f[u] + weight
            if v not in dist_f or new_dist < dist_f[v]:
                dist_f[v] = new_dist
                parent_f[v] = u
                heapq.heappush(pq_f, (new_dist, v))
            if v in visited_b:
                total = dist_f.get(v, float("inf")) + dist_b[v]
                if total < best:
                    best, meeting_node = total, v

    def _relax_backward(u: str) -> None:
        nonlocal best, meeting_node
        for edge in reverse_adjacency[u]:
            v = edge.source 
            weight = edge.get_weight(criterion)
            new_dist = dist_b[u] + weight
            if v not in dist_b or new_dist < dist_b[v]:
                dist_b[v] = new_dist
                parent_b[v] = u
                heapq.heappush(pq_b, (new_dist, v))
            if v in visited_f:
                total = dist_b.get(v, float("inf")) + dist_f[v]
                if total < best:
                    best, meeting_node = total, v

    while pq_f and pq_b:
        if pq_f[0][0] + pq_b[0][0] >= best:
            break 

        if pq_f[0][0] <= pq_b[0][0]:
            d_u, u = heapq.heappop(pq_f)
            if u in visited_f:
                continue
            visited_f.add(u)
            expanded_nodes += 1
            if u in visited_b:
                total = dist_f[u] + dist_b[u]
                if total < best:
                    best, meeting_node = total, u
            _relax_forward(u)
        else:
            d_u, u = heapq.heappop(pq_b)
            if u in visited_b:
                continue
            visited_b.add(u)
            expanded_nodes += 1
            if u in visited_f:
                total = dist_b[u] + dist_f[u]
                if total < best:
                    best, meeting_node = total, u
            _relax_backward(u)

    if meeting_node is None:
        return None, float("inf"), expanded_nodes


    forward_part = [meeting_node]
    node = meeting_node
    while node != source_id:
        node = parent_f[node]
        forward_part.append(node)
    forward_part.reverse()

    backward_part = []
    node = meeting_node
    while node != target_id:
        node = parent_b[node]
        backward_part.append(node)

    return forward_part + backward_part, best, expanded_nodes


def _dijkstra_early_stopping(
    graph: Graph, source_id: str, target_id: str, criterion: str = "distance"
) -> Tuple[Optional[List[str]], float, int]:

    if not graph.has_station(source_id) or not graph.has_station(target_id):
        return None, float("inf"), 0
    if source_id == target_id:
        return [source_id], 0.0, 0

    dist: Dict[str, float] = {source_id: 0.0}
    parent: Dict[str, str] = {}
    visited = set()
    heap: List[Tuple[float, str]] = [(0.0, source_id)]
    expanded_nodes = 0

    while heap:
        d, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        expanded_nodes += 1

        if u == target_id:
            path = [u]
            while path[-1] != source_id:
                path.append(parent[path[-1]])
            path.reverse()
            return path, d, expanded_nodes

        for edge in graph.neighbors(u):
            v = edge.destination
            new_dist = d + edge.get_weight(criterion)
            if v not in dist or new_dist < dist[v]:
                dist[v] = new_dist
                parent[v] = u
                heapq.heappush(heap, (new_dist, v))

    return None, float("inf"), expanded_nodes


def compare_expanded_nodes(
    graph: Graph, source_id: str, target_id: str, criterion: str = "distance"
) -> Dict[str, object]:
 
    uni_path, uni_cost, uni_expanded = _dijkstra_early_stopping(
        graph, source_id, target_id, criterion
    )
    bi_path, bi_cost, bi_expanded = bidirectional_dijkstra(
        graph, source_id, target_id, criterion
    )

    return {
        "unidirectional": {"path": uni_path, "cost": uni_cost, "expanded_nodes": uni_expanded},
        "bidirectional": {"path": bi_path, "cost": bi_cost, "expanded_nodes": bi_expanded},
        "costs_match": uni_cost == bi_cost,
    }
