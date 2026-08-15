import heapq
import itertools
from dataclasses import dataclass
from typing import List

from models.edge import Edge
from models.graph import Graph


@dataclass
class MSTResult:
    edges: List[Edge]
    total_cost: float


def prim(graph: Graph, start=None, criterion="distance"):

    if graph.num_stations() == 0:
        return MSTResult([], 0)

    if start is None:
        start = graph.station_ids()[0]

    visited = {start}

    heap = []
    counter = itertools.count()  

    for edge in graph.neighbors(start):
        heapq.heappush(
            heap,
            (
                edge.get_weight(criterion),
                next(counter),
                edge,
            ),
        )

    mst = []

    total = 0

    while heap and len(visited) < graph.num_stations():

        cost, _tie, edge = heapq.heappop(heap)

        if edge.destination in visited:
            continue

        visited.add(edge.destination)

        mst.append(edge)

        total += cost

        for nxt in graph.neighbors(edge.destination):

            if nxt.destination not in visited:

                heapq.heappush(
                    heap,
                    (
                        nxt.get_weight(criterion),
                        next(counter),
                        nxt,
                    ),
                )

    return MSTResult(
        mst,
        total,
    )