"""
    python3 -m unittest tests/test_network_analysis.py -v
"""

import os
import unittest

from models import Graph, Station
from algorithms.floyd_warshall import floyd_warshall, reconstruct_path, has_negative_cycle
from algorithms.max_flow import max_flow
from algorithms.articulation import find_articulation_points_and_bridges
from algorithms.dominating_set import greedy_dominating_set, is_valid_dominating_set
from algorithms.levenshtein import levenshtein_distance, find_closest_station
from algorithms.dijkstra import dijkstra_shortest_path
from utils.loader import build_graph_from_files, apply_capacities_from_file


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
STATIONS_PATH = os.path.join(DATA_DIR, "stations.txt")
EDGES_PATH = os.path.join(DATA_DIR, "edges.txt")
CAPACITY_PATH = os.path.join(DATA_DIR, "capacity.txt")


def build_qom_graph() -> Graph:
    return build_graph_from_files(STATIONS_PATH, EDGES_PATH)


class TestFloydWarshall(unittest.TestCase):
    def setUp(self):
        self.g = build_qom_graph()

    def test_diagonal_is_zero(self):
        _ids, dist, _next_hop = floyd_warshall(self.g, criterion="distance")
        for i in range(len(dist)):
            self.assertEqual(dist[i][i], 0)

    def test_matches_dijkstra_on_a_pair(self):
        ids, dist, next_hop = floyd_warshall(self.g, criterion="distance")
        index_of = {sid: i for i, sid in enumerate(ids)}

        start = "ایستگاه ترمینال مسافربری قم"
        goal = "ایستگاه بوستان جنگلی غدیر"

        _dijkstra_path, dijkstra_cost = dijkstra_shortest_path(self.g, start, goal, "distance")
        fw_cost = dist[index_of[start]][index_of[goal]]

        self.assertAlmostEqual(fw_cost, dijkstra_cost)

    def test_reconstruct_path_matches_cost(self):
        ids, dist, next_hop = floyd_warshall(self.g, criterion="distance")
        start = "ایستگاه ترمینال مسافربری قم"
        goal = "ایستگاه راه آهن قم"

        path = reconstruct_path(ids, next_hop, start, goal)
        self.assertIsNotNone(path)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)
    
        for a, b in zip(path, path[1:]):
            self.assertTrue(self.g.has_edge(a, b))

    def test_small_graph_with_no_negative_cycle(self):
        g = Graph(directed=False)
        g.add_edge("A", "B", distance=1, time=1)
        g.add_edge("B", "C", distance=1, time=1)
        _ids, dist, _next_hop = floyd_warshall(g)
        self.assertFalse(has_negative_cycle(dist))


class TestMaxFlow(unittest.TestCase):
    def test_simple_diamond_network(self):
  
        g = Graph(directed=True)
        g.add_edge("S", "A", capacity=5)
        g.add_edge("A", "T", capacity=5)
        g.add_edge("S", "B", capacity=5)
        g.add_edge("B", "T", capacity=5)

        result = max_flow(g, "S", "T")
        self.assertEqual(result, 10)

    def test_bottleneck_limits_flow(self):
        
        g = Graph(directed=True)
        g.add_edge("S", "A", capacity=10)
        g.add_edge("A", "T", capacity=2)

        self.assertEqual(max_flow(g, "S", "T"), 2)

    def test_no_path_gives_zero_flow(self):
        g = Graph(directed=True)
        g.add_edge("S", "A", capacity=10)
        g.add_station(Station("T")) 

        self.assertEqual(max_flow(g, "S", "T"), 0)

    def test_same_source_and_sink(self):
        g = Graph(directed=True)
        g.add_edge("S", "A", capacity=10)
        self.assertEqual(max_flow(g, "S", "S"), 0)

    def test_on_real_qom_graph_with_capacities(self):
        g = build_qom_graph()
        apply_capacities_from_file(g, CAPACITY_PATH)

        flow_value = max_flow(
            g,
            "ایستگاه ترمینال مسافربری قم",
            "ایستگاه بوستان جنگلی غدیر",
        )
        self.assertGreater(flow_value, 0)


class TestArticulation(unittest.TestCase):
    def test_path_graph(self):

        g = Graph(directed=False)
        g.add_edge("A", "B", distance=1, time=1)
        g.add_edge("B", "C", distance=1, time=1)
        g.add_edge("C", "D", distance=1, time=1)

        points, bridges = find_articulation_points_and_bridges(g)
        self.assertEqual(points, {"B", "C"})
        self.assertEqual(len(bridges), 3)

    def test_cycle_graph_has_no_articulation_points(self):
  
        g = Graph(directed=False)
        g.add_edge("A", "B", distance=1, time=1)
        g.add_edge("B", "C", distance=1, time=1)
        g.add_edge("C", "D", distance=1, time=1)
        g.add_edge("D", "A", distance=1, time=1)

        points, bridges = find_articulation_points_and_bridges(g)
        self.assertEqual(points, set())
        self.assertEqual(bridges, [])

    def test_star_graph_center_is_articulation_point(self):

        g = Graph(directed=False)
        g.add_edge("Center", "Leaf1", distance=1, time=1)
        g.add_edge("Center", "Leaf2", distance=1, time=1)
        g.add_edge("Center", "Leaf3", distance=1, time=1)

        points, bridges = find_articulation_points_and_bridges(g)
        self.assertIn("Center", points)
        self.assertEqual(len(bridges), 3)

    def test_on_real_qom_graph(self):
        g = build_qom_graph()
        points, bridges = find_articulation_points_and_bridges(g)
  
        self.assertGreater(len(points), 0)
        self.assertGreater(len(bridges), 0)



class TestDominatingSet(unittest.TestCase):
    def test_result_is_valid_on_path_graph(self):
        g = Graph(directed=False)
        g.add_edge("A", "B", distance=1, time=1)
        g.add_edge("B", "C", distance=1, time=1)
        g.add_edge("C", "D", distance=1, time=1)
        g.add_edge("D", "E", distance=1, time=1)

        solution = greedy_dominating_set(g)
        self.assertTrue(is_valid_dominating_set(g, solution))
        
        self.assertLessEqual(len(solution), 3)

    def test_result_is_valid_on_real_qom_graph(self):
        g = build_qom_graph()
        solution = greedy_dominating_set(g)

        self.assertTrue(is_valid_dominating_set(g, solution))
        self.assertLess(len(solution), g.num_stations())

    def test_single_station_graph(self):
        g = Graph(directed=False)
        g.add_station(Station("Only"))
        solution = greedy_dominating_set(g)
        self.assertEqual(solution, ["Only"])



class TestLevenshtein(unittest.TestCase):
    def test_identical_strings(self):
        self.assertEqual(levenshtein_distance("قلعه کامکار", "قلعه کامکار"), 0)

    def test_one_substitution(self):
        self.assertEqual(levenshtein_distance("cat", "cot"), 1)

    def test_one_insertion(self):
        self.assertEqual(levenshtein_distance("cat", "cats"), 1)

    def test_empty_strings(self):
        self.assertEqual(levenshtein_distance("", ""), 0)
        self.assertEqual(levenshtein_distance("abc", ""), 3)

    def test_find_closest_station_with_typo(self):
        names = [
            "ایستگاه میدان مطهری",
            "ایستگاه میدان کشاورز",
            "ایستگاه بیمارستان نکویی",
        ]
        
        query = "ایستگاه میدان متهری"
        results = find_closest_station(query, names, max_results=1)

        self.assertEqual(results[0][0], "ایستگاه میدان مطهری")

    def test_find_closest_station_returns_sorted_and_limited(self):
        names = ["abc", "abd", "xyz"]
        results = find_closest_station("abc", names, max_results=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], ("abc", 0))


if __name__ == "__main__":
    unittest.main()
