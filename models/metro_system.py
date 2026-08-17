from algorithms.bfs import bfs_shortest_path
from algorithms.dijkstra import dijkstra_shortest_path
from algorithms.prim import prim
from algorithms.kruskal import kruskal

from models.graph import Graph


class MetroSystem:
    def __init__(self, graph: Graph):

        self.graph = graph

    def reachable(self, start, goal):

        return bfs_shortest_path(
            self.graph,
            start,
            goal,
        )

    def shortest_path(
        self,
        start,
        goal,
        criterion="distance",
    ):

        return dijkstra_shortest_path(
            self.graph,
            start,
            goal,
            criterion,
        )

    def mst_prim(
        self,
        criterion="distance",
    ):

        return prim(
            self.graph,
            criterion=criterion,
        )

    def mst_kruskal(
        self,
        criterion="distance",
    ):

        return kruskal(
            self.graph,
            criterion,
        )
