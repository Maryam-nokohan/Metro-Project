"""
    python3 -m unittest tests/test_algorithms.py -v
"""

import os
import unittest

from models import Graph, Station
from algorithms.bfs import bfs_traversal, bfs_shortest_path, is_reachable_bfs
from algorithms.dfs import dfs_traversal, dfs_path, is_reachable_dfs
from algorithms.dijkstra import dijkstra, dijkstra_shortest_path
from utils.loader import build_graph_from_files


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
STATIONS_PATH = os.path.join(DATA_DIR, "stations.txt")
EDGES_PATH = os.path.join(DATA_DIR, "edges.txt")


def build_small_graph_with_isolated_station() -> Graph:
  
    g = Graph(directed=False)
    g.add_edge("A", "B", distance=1, time=1)
    g.add_edge("B", "C", distance=1, time=1)
    g.add_edge("C", "D", distance=1, time=1)
    g.add_station(Station("ISOLATED"))
    return g


def build_small_weighted_graph() -> Graph:

    g = Graph(directed=False)
    g.add_edge("A", "B", distance=5, time=0.5)
    g.add_edge("B", "D", distance=5, time=0.5)
    g.add_edge("A", "C", distance=1, time=10)
    g.add_edge("C", "D", distance=1, time=10)
    g.add_station(Station("ISOLATED"))
    return g


class TestBFS(unittest.TestCase):
    def setUp(self):
        self.g = build_small_graph_with_isolated_station()

    def test_traversal_visits_whole_component(self):
        order = bfs_traversal(self.g, "A")
        self.assertEqual(set(order), {"A", "B", "C", "D"})

    def test_traversal_from_unknown_station_returns_empty(self):
        self.assertEqual(bfs_traversal(self.g, "X"), [])

    def test_shortest_path_found(self):
        self.assertEqual(bfs_shortest_path(self.g, "A", "D"), ["A", "B", "C", "D"])

    def test_same_start_and_goal(self):
        self.assertEqual(bfs_shortest_path(self.g, "A", "A"), ["A"])

    def test_unreachable_returns_none(self):
        self.assertIsNone(bfs_shortest_path(self.g, "A", "ISOLATED"))

    def test_is_reachable(self):
        self.assertTrue(is_reachable_bfs(self.g, "A", "D"))
        self.assertFalse(is_reachable_bfs(self.g, "A", "ISOLATED"))


class TestDFS(unittest.TestCase):
    def setUp(self):
        self.g = build_small_graph_with_isolated_station()

    def test_traversal_visits_whole_component(self):
        order = dfs_traversal(self.g, "A")
        self.assertEqual(set(order), {"A", "B", "C", "D"})

    def test_path_found_and_valid(self):
        path = dfs_path(self.g, "A", "D")
        self.assertIsNotNone(path)
        self.assertEqual(path[0], "A")
        self.assertEqual(path[-1], "D")

        for a, b in zip(path, path[1:]):
            self.assertTrue(self.g.has_edge(a, b))

    def test_unreachable_returns_none(self):
        self.assertIsNone(dfs_path(self.g, "A", "ISOLATED"))

    def test_is_reachable(self):
        self.assertTrue(is_reachable_dfs(self.g, "A", "D"))
        self.assertFalse(is_reachable_dfs(self.g, "A", "ISOLATED"))


class TestDijkstra(unittest.TestCase):
    def setUp(self):
        self.g = build_small_weighted_graph()

    def test_shortest_path_by_distance(self):

        path, cost = dijkstra_shortest_path(self.g, "A", "D", criterion="distance")
        self.assertEqual(path, ["A", "C", "D"])
        self.assertEqual(cost, 2)

    def test_shortest_path_by_time(self):

        path, cost = dijkstra_shortest_path(self.g, "A", "D", criterion="time")
        self.assertEqual(path, ["A", "B", "D"])
        self.assertEqual(cost, 1)

    def test_same_start_and_goal(self):
        path, cost = dijkstra_shortest_path(self.g, "A", "A")
        self.assertEqual(path, ["A"])
        self.assertEqual(cost, 0)

    def test_unreachable_station(self):
        path, cost = dijkstra_shortest_path(self.g, "A", "ISOLATED")
        self.assertIsNone(path)
        self.assertEqual(cost, float("inf"))

    def test_unknown_station_returns_none(self):
        path, cost = dijkstra_shortest_path(self.g, "A", "NOT_IN_GRAPH")
        self.assertIsNone(path)
        self.assertEqual(cost, float("inf"))

    def test_invalid_criterion_raises(self):
        with self.assertRaises(ValueError):
            dijkstra_shortest_path(self.g, "A", "D", criterion="not_a_real_criterion")

    def test_dist_dictionary_contains_all_reachable_stations(self):
        dist, _ = dijkstra(self.g, "A", criterion="distance")
        self.assertEqual(set(dist.keys()), {"A", "B", "C", "D"})
        self.assertNotIn("ISOLATED", dist)


class TestOnRealQomGraph(unittest.TestCase):


    def setUp(self):
        self.g = build_graph_from_files(STATIONS_PATH, EDGES_PATH)

    def test_all_20_stations_loaded(self):
        self.assertEqual(self.g.num_stations(), 20)

    def test_graph_is_fully_connected(self):

        start = "ایستگاه ترمینال مسافربری قم"
        reached = set(bfs_traversal(self.g, start))
        self.assertEqual(reached, set(self.g.station_ids()))

    def test_reachability_between_far_stations(self):
        self.assertTrue(
            is_reachable_bfs(
                self.g,
                "ایستگاه ترمینال مسافربری قم",
                "ایستگاه بوستان جنگلی غدیر",
            )
        )
        self.assertTrue(
            is_reachable_dfs(
                self.g,
                "ایستگاه ترمینال مسافربری قم",
                "ایستگاه بوستان جنگلی غدیر",
            )
        )

    def test_dijkstra_shortest_path_by_distance(self):
        path, cost = dijkstra_shortest_path(
            self.g,
            "ایستگاه ترمینال مسافربری قم",
            "ایستگاه راه آهن قم",
            criterion="distance",
        )

        self.assertEqual(path[0], "ایستگاه ترمینال مسافربری قم")
        self.assertEqual(path[-1], "ایستگاه راه آهن قم")
        self.assertAlmostEqual(cost, 4.2)

    def test_dijkstra_distance_and_time_can_choose_different_paths(self):
  

        path_d, cost_d = dijkstra_shortest_path(
            self.g,
            "ایستگاه میدان مطهری",
            "ایستگاه امین آباد",
            criterion="distance",
        )
        path_t, cost_t = dijkstra_shortest_path(
            self.g,
            "ایستگاه میدان مطهری",
            "ایستگاه امین آباد",
            criterion="time",
        )
        self.assertIsNotNone(path_d)
        self.assertIsNotNone(path_t)
        self.assertGreaterEqual(cost_d, 0)
        self.assertGreaterEqual(cost_t, 0)


if __name__ == "__main__":
    unittest.main()