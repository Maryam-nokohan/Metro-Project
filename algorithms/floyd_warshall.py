from typing import List, Optional, Tuple

from models.graph import Graph


def floyd_warshall(
    graph: Graph, criterion: str = "distance"
) -> Tuple[List[str], List[List[float]], List[List[Optional[int]]]]:

    station_ids, dist = graph.to_adjacency_matrix(criterion=criterion)
    n = len(station_ids)

    next_hop: List[List[Optional[int]]] = [
        [j if dist[i][j] != float("inf") else None for j in range(n)]
        for i in range(n)
    ]

    for k in range(n):
        for i in range(n):
            if dist[i][k] == float("inf"):
                continue
            dist_ik = dist[i][k]
            for j in range(n):
                through_k = dist_ik + dist[k][j]
                if through_k < dist[i][j]:
                    dist[i][j] = through_k
                    next_hop[i][j] = next_hop[i][k]

    return station_ids, dist, next_hop


def reconstruct_path(
    station_ids: List[str],
    next_hop: List[List[Optional[int]]],
    start_id: str,
    goal_id: str,
) -> Optional[List[str]]:
 
    index_of = {sid: i for i, sid in enumerate(station_ids)}
    if start_id not in index_of or goal_id not in index_of:
        return None

    i, j = index_of[start_id], index_of[goal_id]
    if next_hop[i][j] is None:
        return None

    path_indices = [i]
    while i != j:
        i = next_hop[i][j]
        path_indices.append(i)

    return [station_ids[idx] for idx in path_indices]


def has_negative_cycle(dist: List[List[float]]) -> bool:

    return any(dist[i][i] < 0 for i in range(len(dist)))