import unittest

from models.graph import Graph

from algorithms.kruskal import kruskal
from algorithms.prim import prim


class TestMST(unittest.TestCase):
    def setUp(self):

        self.g = Graph()

        self.g.add_edge("A", "B", distance=1)

        self.g.add_edge("A", "C", distance=5)

        self.g.add_edge("B", "C", distance=2)

        self.g.add_edge("B", "D", distance=3)

        self.g.add_edge("C", "D", distance=4)

    def test_kruskal(self):

        mst = kruskal(self.g)

        self.assertEqual(len(mst.edges), 3)

        self.assertEqual(mst.total_cost, 6)

    def test_prim(self):

        mst = prim(self.g)

        self.assertEqual(len(mst.edges), 3)

        self.assertEqual(mst.total_cost, 6)


if __name__ == "__main__":
    unittest.main()
