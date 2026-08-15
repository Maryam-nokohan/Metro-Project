from typing import Dict, List, Optional, Tuple

from models.graph import Graph


def bellman_ford(
    graph: Graph,
    start: str,
    criterion: str = "weight",
):
    """
    Returns:
        dist
        parent
        negative_cycle
    """

    dist = {
        station: float("inf")
        for station in graph.station_ids()
    }

    parent = {}

    dist[start] = 0

    n = graph.num_stations()

    for _ in range(n - 1):

        updated = False

        for u in graph.station_ids():
            for edge in graph.neighbors(u):

                v = edge.destination

                w = edge.get_weight(criterion)

                if dist[u] == float("inf"):
                    continue

                if dist[u] + w < dist[v]:

                    dist[v] = dist[u] + w

                    parent[v] = u

                    updated = True

        if not updated:
            break

    negative_cycle = []

    for u in graph.station_ids():
        for edge in graph.neighbors(u):

            v = edge.destination

            w = edge.get_weight(criterion)

            if dist[u] != float("inf"):

                if dist[u] + w < dist[v]:

                    negative_cycle.append(
                        (u, v)
                    )

    return dist, parent, negative_cycle