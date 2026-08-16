import os
import unittest

from models import Graph
from algorithms.bidirectional_dijkstra import (
    bidirectional_dijkstra,
    compare_expanded_nodes,
)
from algorithms.dijkstra import dijkstra_shortest_path
from utils.loader import build_graph_from_files


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
STATIONS_PATH = os.path.join(DATA_DIR, "stations.txt")
EDGES_PATH = os.path.join(DATA_DIR, "edges.txt")


def build_qom_graph() -> Graph:
    return build_graph_from_files(STATIONS_PATH, EDGES_PATH)


class TestBidirectionalDijkstraSmallGraph(unittest.TestCase):
    def setUp(self):

        self.g = Graph(directed=False)
        self.g.add_edge("A", "B", distance=1, time=1)
        self.g.add_edge("B", "C", distance=1, time=1)
        self.g.add_edge("C", "D", distance=1, time=1)
        self.g.add_edge("D", "E", distance=1, time=1)

    def test_correct_cost_and_endpoints(self):
        path, cost, _expanded = bidirectional_dijkstra(self.g, "A", "E")
        self.assertEqual(cost, 4)
        self.assertEqual(path[0], "A")
        self.assertEqual(path[-1], "E")
        self.assertEqual(len(path), 5)

    def test_path_edges_are_all_valid(self):
        path, _cost, _expanded = bidirectional_dijkstra(self.g, "A", "E")
        for u, v in zip(path, path[1:]):
            self.assertTrue(self.g.has_edge(u, v))

    def test_same_source_and_target(self):
        path, cost, expanded = bidirectional_dijkstra(self.g, "A", "A")
        self.assertEqual(path, ["A"])
        self.assertEqual(cost, 0)
        self.assertEqual(expanded, 0)

    def test_unreachable_target(self):
        from models.station import Station

        self.g.add_station(Station("ISOLATED"))
        path, cost, _expanded = bidirectional_dijkstra(self.g, "A", "ISOLATED")
        self.assertIsNone(path)
        self.assertEqual(cost, float("inf"))

    def test_unknown_station_returns_none(self):
        path, cost, _expanded = bidirectional_dijkstra(self.g, "A", "NOT_A_STATION")
        self.assertIsNone(path)
        self.assertEqual(cost, float("inf"))


class TestBidirectionalDijkstraDirectedGraph(unittest.TestCase):
    def setUp(self):
        self.g = Graph(directed=False)

        self.g.add_edge("X", "Y", distance=1, time=1, directed=True)
        self.g.add_edge("Y", "Z", distance=1, time=1, directed=True)

    def test_forward_direction_works(self):
        path, cost, _expanded = bidirectional_dijkstra(self.g, "X", "Z")
        self.assertEqual(path, ["X", "Y", "Z"])
        self.assertEqual(cost, 2)

    def test_backward_direction_is_blocked(self):

        path, cost, _expanded = bidirectional_dijkstra(self.g, "Z", "X")
        self.assertIsNone(path)
        self.assertEqual(cost, float("inf"))


class TestBidirectionalDijkstraOnRealQomGraph(unittest.TestCase):
    def setUp(self):
        self.g = build_qom_graph()

    def test_cost_matches_standard_dijkstra(self):
        pairs = [
            ("ایستگاه ترمینال مسافربری قم", "ایستگاه بوستان جنگلی غدیر"),
            ("ایستگاه میدان مطهری", "ایستگاه امین آباد"),
            ("ایستگاه راه آهن قم", "ایستگاه مسجد مقدس جمکران"),
        ]
        for source, target in pairs:
            with self.subTest(source=source, target=target):
                _uni_path, uni_cost = dijkstra_shortest_path(
                    self.g, source, target, criterion="distance"
                )
                _bi_path, bi_cost, _expanded = bidirectional_dijkstra(
                    self.g, source, target, criterion="distance"
                )
                self.assertAlmostEqual(uni_cost, bi_cost)

    def test_compare_expanded_nodes_reports_matching_costs(self):
        result = compare_expanded_nodes(
            self.g,
            "ایستگاه ترمینال مسافربری قم",
            "ایستگاه بوستان جنگلی غدیر",
            criterion="distance",
        )
        self.assertTrue(result["costs_match"])
        self.assertGreater(result["unidirectional"]["expanded_nodes"], 0)
        self.assertGreater(result["bidirectional"]["expanded_nodes"], 0)


if __name__ == "__main__":
    unittest.main()
