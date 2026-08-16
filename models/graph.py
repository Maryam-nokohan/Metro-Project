from __future__ import annotations
from typing import Dict, List, Optional, Tuple

from models.station import Station
from models.edge import Edge


class Graph:
    def __init__(self, directed: bool = False) -> None:
        self.directed: bool = directed
        self._stations: Dict[str, Station] = {}
        self._adjacency: Dict[str, List[Edge]] = {}

    def add_station(self, station: Station) -> Station:

        if station.station_id not in self._stations:
            self._stations[station.station_id] = station
            self._adjacency[station.station_id] = []
        return self._stations[station.station_id]

    def get_station(self, station_id: str) -> Optional[Station]:
        return self._stations.get(station_id)

    def has_station(self, station_id: str) -> bool:
        return station_id in self._stations

    def stations(self) -> List[Station]:

        return list(self._stations.values())

    def station_ids(self) -> List[str]:
        return list(self._stations.keys())

    def num_stations(self) -> int:
        return len(self._stations)

    def add_edge(
        self,
        source_id: str,
        destination_id: str,
        distance: float = 0.0,
        time: float = 0.0,
        directed: Optional[bool] = None,
        weight: Optional[float] = None,
        capacity: Optional[float] = None,
    ) -> Edge:

        if source_id not in self._stations:
            self.add_station(Station(source_id))
        if destination_id not in self._stations:
            self.add_station(Station(destination_id))

        is_directed = self.directed if directed is None else directed

        edge = Edge(
            source=source_id,
            destination=destination_id,
            distance=distance,
            time=time,
            directed=is_directed,
            weight=weight,
            capacity=capacity,
        )
        self._adjacency[source_id].append(edge)

        if not is_directed:
            self._adjacency[destination_id].append(edge.reversed())

        return edge

    def get_edge(self, source_id: str, destination_id: str) -> Optional[Edge]:

        for edge in self._adjacency.get(source_id, []):
            if edge.destination == destination_id:
                return edge
        return None

    def has_edge(self, source_id: str, destination_id: str) -> bool:
        return self.get_edge(source_id, destination_id) is not None

    def remove_edge(self, source_id: str, destination_id: str) -> bool:

        removed = False
        edges = self._adjacency.get(source_id, [])
        for edge in list(edges):
            if edge.destination == destination_id:
                edges.remove(edge)
                removed = True
                if not edge.directed:
                    back_edges = self._adjacency.get(destination_id, [])
                    for back_edge in list(back_edges):
                        if back_edge.destination == source_id:
                            back_edges.remove(back_edge)
                            break
        return removed

    def neighbors(self, station_id: str) -> List[Edge]:

        return list(self._adjacency.get(station_id, []))

    def edges(self) -> List[Edge]:

        seen: List[Edge] = []
        seen_pairs = set()
        for station_id, edge_list in self._adjacency.items():
            for edge in edge_list:
                if edge.directed:
                    key = (edge.source, edge.destination, True)
                    if key not in seen_pairs:
                        seen_pairs.add(key)
                        seen.append(edge)
                else:
                    key = frozenset((edge.source, edge.destination))
                    if key not in seen_pairs:
                        seen_pairs.add(key)
                        seen.append(edge)
        return seen

    def num_edges(self) -> int:
        return len(self.edges())

    def to_adjacency_matrix(
        self, criterion: str = "distance", default: float = float("inf")
    ) -> Tuple[List[str], List[List[float]]]:

        ids = self.station_ids()
        index_of = {station_id: i for i, station_id in enumerate(ids)}
        n = len(ids)
        matrix = [[default] * n for _ in range(n)]
        for i in range(n):
            matrix[i][i] = 0.0

        for station_id in ids:
            for edge in self._adjacency[station_id]:
                i, j = index_of[edge.source], index_of[edge.destination]
                w = edge.get_weight(criterion)
                if w < matrix[i][j]:
                    matrix[i][j] = w

        return ids, matrix

    def __contains__(self, station_id: str) -> bool:
        return station_id in self._stations

    def __repr__(self) -> str:
        return (
            f"Graph(directed={self.directed}, "
            f"stations={self.num_stations()}, edges={self.num_edges()})"
        )
