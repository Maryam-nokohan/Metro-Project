"""
python -m unittest tests/test_graph.py -v
"""

import unittest

from models import Station, Edge, Graph


def build_sample_qom_graph() -> Graph:

    g = Graph(directed=False)
    edges = [
        ("ترمینال مسافربری قم", "قلعه کامکار", 1.2, 3),
        ("قلعه کامکار", "میدان کشاورز", 2.5, 5),
        ("میدان کشاورز", "میدان مطهری", 6, 10),
        ("میدان مطهری", "بیمارستان نکویی", 3, 5),
        ("بیمارستان نکویی", "میدان بقیه الله", 2, 4),
        ("میدان مطهری", "حرم مطهر حضرت معصومه (س)", 4, 1.5),
        ("حرم مطهر حضرت معصومه (س)", "ارگ سالاریه", 1, 3),
        ("قلعه کامکار", "راه آهن قم", 3, 5),
    ]
    for source, destination, distance, time in edges:
        g.add_edge(source, destination, distance=distance, time=time)
    return g


class TestStation(unittest.TestCase):
    def test_default_name_equals_id(self):
        s = Station("A")
        self.assertEqual(s.name, "A")

    def test_equality_and_hash_based_on_id(self):
        s1 = Station("A", name="ایستگاه ۱")
        s2 = Station("A", name="نام دیگر")
        self.assertEqual(s1, s2)
        self.assertEqual(hash(s1), hash(s2))

    def test_empty_id_raises(self):
        with self.assertRaises(ValueError):
            Station("")


class TestEdge(unittest.TestCase):
    def test_get_weight_by_criterion(self):
        e = Edge("A", "B", distance=5, time=10)
        self.assertEqual(e.get_weight("distance"), 5)
        self.assertEqual(e.get_weight("time"), 10)

    def test_weight_fallback_to_distance(self):
        e = Edge("A", "B", distance=5, time=10)
        self.assertEqual(e.get_weight("weight"), 5)

    def test_custom_weight_used_when_given(self):
        e = Edge("A", "B", distance=5, time=10, weight=-2)
        self.assertEqual(e.get_weight("weight"), -2)

    def test_self_loop_not_allowed(self):
        with self.assertRaises(ValueError):
            Edge("A", "A")

    def test_reversed_edge(self):
        e = Edge("A", "B", distance=5, time=10)
        r = e.reversed()
        self.assertEqual(r.source, "B")
        self.assertEqual(r.destination, "A")
        self.assertEqual(r.distance, e.distance)


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.g = build_sample_qom_graph()

    def test_stations_auto_created_from_edges(self):
        self.assertTrue(self.g.has_station("قلعه کامکار"))
        self.assertTrue(self.g.has_station("راه آهن قم"))
        self.assertEqual(self.g.num_stations(), 9)

    def test_undirected_edge_visible_from_both_sides(self):
        self.assertTrue(self.g.has_edge("قلعه کامکار", "میدان کشاورز"))
        self.assertTrue(self.g.has_edge("میدان کشاورز", "قلعه کامکار"))

    def test_edge_weight_values(self):
        e = self.g.get_edge("میدان کشاورز", "میدان مطهری")
        self.assertEqual(e.distance, 6)
        self.assertEqual(e.time, 10)

    def test_neighbors_count(self):

        neighbor_ids = {e.destination for e in self.g.neighbors("میدان مطهری")}
        self.assertEqual(
            neighbor_ids,
            {"میدان کشاورز", "بیمارستان نکویی", "حرم مطهر حضرت معصومه (س)"},
        )

    def test_directed_edge_only_one_way(self):
        g = Graph(directed=False)
        g.add_edge("X", "Y", distance=1, time=1, directed=True)
        self.assertTrue(g.has_edge("X", "Y"))
        self.assertFalse(g.has_edge("Y", "X"))

    def test_remove_edge(self):
        removed = self.g.remove_edge("قلعه کامکار", "میدان کشاورز")
        self.assertTrue(removed)
        self.assertFalse(self.g.has_edge("قلعه کامکار", "میدان کشاورز"))
        self.assertFalse(self.g.has_edge("میدان کشاورز", "قلعه کامکار"))

    def test_num_edges_no_double_count_for_undirected(self):

        self.assertEqual(self.g.num_edges(), 8)

    def test_to_adjacency_matrix_shape_and_diagonal(self):
        ids, matrix = self.g.to_adjacency_matrix(criterion="distance")
        n = len(ids)
        self.assertEqual(len(matrix), n)
        self.assertEqual(len(matrix[0]), n)
        for i in range(n):
            self.assertEqual(matrix[i][i], 0.0)


if __name__ == "__main__":
    unittest.main()
