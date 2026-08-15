from typing import Dict, List, Set, Tuple

from models.graph import Graph


def find_articulation_points_and_bridges(
    graph: Graph,
) -> Tuple[Set[str], List[Tuple[str, str]]]:

    disc: Dict[str, int] = {}
    low: Dict[str, int] = {}
    parent: Dict[str, str] = {}
    articulation_points: Set[str] = set()
    bridges: List[Tuple[str, str]] = []
    timer = 0

    for root in graph.station_ids():
        if root in disc:
            continue

        stack = [(root, iter(graph.neighbors(root)))]
        disc[root] = low[root] = timer
        timer += 1
        root_children = 0

        while stack:
            u, neighbor_iter = stack[-1]
            descended = False

            for edge in neighbor_iter:
                v = edge.destination
                if v == parent.get(u):

                    continue

                if v not in disc:
                    parent[v] = u
                    disc[v] = low[v] = timer
                    timer += 1
                    if u == root:
                        root_children += 1
                    stack.append((v, iter(graph.neighbors(v))))
                    descended = True
                    break
                else:

                    low[u] = min(low[u], disc[v])

            if descended:
                continue

            stack.pop()
            if not stack:
                continue

            p = stack[-1][0]
            low[p] = min(low[p], low[u])

            if p != root and low[u] >= disc[p]:
                articulation_points.add(p)

            if low[u] > disc[p]:
                bridges.append((p, u))

        if root_children > 1:
            articulation_points.add(root)

    return articulation_points, bridges