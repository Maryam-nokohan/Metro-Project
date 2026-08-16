from typing import Dict, List, Set

from models.graph import Graph


def _coverage_set(graph: Graph, station_id: str) -> Set[str]:

    covered = {station_id}
    for edge in graph.neighbors(station_id):
        covered.add(edge.destination)
    return covered


def greedy_dominating_set(graph: Graph) -> List[str]:

    all_stations = set(graph.station_ids())
    uncovered = set(all_stations)
    coverage: Dict[str, Set[str]] = {
        station_id: _coverage_set(graph, station_id) for station_id in all_stations
    }

    solution: List[str] = []

    while uncovered:
        best_station = max(all_stations, key=lambda s: len(coverage[s] & uncovered))
        newly_covered = coverage[best_station] & uncovered

        if not newly_covered:
            leftover = next(iter(uncovered))
            solution.append(leftover)
            uncovered.discard(leftover)
            continue

        solution.append(best_station)
        uncovered -= newly_covered

    return solution


def is_valid_dominating_set(graph: Graph, candidate: List[str]) -> bool:

    covered: Set[str] = set()
    for station_id in candidate:
        covered |= _coverage_set(graph, station_id)
    return covered >= set(graph.station_ids())
