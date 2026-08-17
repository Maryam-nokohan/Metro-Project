from dataclasses import dataclass
from typing import List

from models.edge import Edge
from models.graph import Graph
from utils.disjoint_set import DisjointSet


@dataclass
class MSTResult:
    edges: List[Edge]
    total_cost: float


def kruskal(
    graph: Graph,
    criterion: str = "distance",
) -> MSTResult:
    if graph.directed:
        raise ValueError("Kruskal برای گراف بدون جهت استفاده می‌شود.")

    stations = graph.station_ids()

    if not stations:
        return MSTResult([], 0.0)

    ds = DisjointSet()

    for station in stations:
        ds.make_set(station)

    sorted_edges = sorted(
        graph.edges(),
        key=lambda edge: edge.get_weight(criterion),
    )

    mst: List[Edge] = []
    total = 0.0

    for edge in sorted_edges:
        if ds.union(
            edge.source,
            edge.destination,
        ):
            mst.append(edge)
            total += edge.get_weight(criterion)

            if len(mst) == len(stations) - 1:
                break

    if len(mst) != len(stations) - 1:
        raise ValueError("گراف متصل نیست؛ بنابراین MST کامل وجود ندارد.")

    return MSTResult(
        edges=mst,
        total_cost=total,
    )
