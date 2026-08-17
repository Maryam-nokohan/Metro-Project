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


def prim(
    graph: Graph,
    start: str | None = None,
    criterion: str = "distance",
) -> MSTResult:
    if graph.directed:
        raise ValueError("Prim برای گراف بدون جهت استفاده می‌شود.")

    station_ids = graph.station_ids()

    if not station_ids:
        return MSTResult([], 0.0)

    if start is None:
        start = station_ids[0]

    if not graph.has_station(start):
        raise ValueError(f"ایستگاه شروع وجود ندارد: {start}")

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

    mst: List[Edge] = []
    total = 0.0

    while heap and len(visited) < len(station_ids):
        cost, _tie, edge = heapq.heappop(heap)

        if edge.destination in visited:
            continue

        visited.add(edge.destination)
        mst.append(edge)
        total += cost

        for next_edge in graph.neighbors(edge.destination):
            if next_edge.destination not in visited:
                heapq.heappush(
                    heap,
                    (
                        next_edge.get_weight(criterion),
                        next(counter),
                        next_edge,
                    ),
                )

    if len(visited) != len(station_ids):
        raise ValueError("گراف متصل نیست؛ بنابراین MST کامل وجود ندارد.")

    return MSTResult(
        edges=mst,
        total_cost=total,
    )
