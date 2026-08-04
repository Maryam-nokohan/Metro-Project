from dataclasses import dataclass
from typing import List

from models.edge import Edge
from models.graph import Graph
from utils.disjoint_set import DisjointSet


@dataclass
class MSTResult:
    edges: List[Edge]
    total_cost: float


def kruskal(graph: Graph, criterion="distance") -> MSTResult:

    ds = DisjointSet()

    for station in graph.station_ids():
        ds.make_set(station)

    edges = sorted(
        graph.edges(),
        key=lambda edge: edge.get_weight(criterion),
    )

    mst = []
    total = 0

    for edge in edges:

        if ds.union(edge.source, edge.destination):
            mst.append(edge)
            total += edge.get_weight(criterion)

    return MSTResult(
        edges=mst,
        total_cost=total,
    )