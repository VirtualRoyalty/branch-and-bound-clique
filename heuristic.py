import numpy as np
import networkx as nx
from utils import *
from run_test import *
from problem import ProblemHandler


class HeuristicMaxClique:

    def __init__(self, graph: nx.Graph):
        self.graph = graph
        self.strategies = [
            self.largest_first_randomized,
            self.color_first_randomized
        ]
        self.coloring_strategies = ProblemHandler.STRATEGIES

    def run(self):
        best_clique_size = 0
        best_clique = None
        for strategy in self.strategies:
            for coloring_strategy in self.coloring_strategies:
                found_clique = strategy(self.graph, strategy=coloring_strategy)
                if best_clique_size < len(found_clique):
                    best_clique_size = len(found_clique)
                    best_clique = found_clique
        return [1.0 if i + 1 in best_clique else 0.0
                for i in range(self.graph.number_of_nodes())]

    @staticmethod
    def color_first_randomized(graph: nx.Graph, n_iterations: int = 20, k_first: int = 3,
                               strategy=nx.coloring.strategy_random_sequential):

        coloring_dct = nx.coloring.greedy_color(graph, strategy=strategy)
        sorted_coloring = sorted(coloring_dct.items(), key=lambda item: item[1], reverse=True)
        nodes = [node for node, color in sorted_coloring]
        best_clique = set()
        best_clique_size = 0
        for _ in range(n_iterations):
            clique = set()
            while len(nodes) > 0:
                random_index = np.random.randint(0, min(k_first, len(nodes)))
                neighbors = list(graph.neighbors(nodes[random_index]))
                clique.add(nodes[random_index])
                nodes = list(filter(lambda x: x in neighbors, nodes))
            if len(clique) > best_clique_size:
                best_clique = clique
                best_clique_size = len(clique)
        return best_clique

    @staticmethod
    def largest_first(graph: nx.Graph, **kwargs):
        clique = set()
        degrees = nx.degree(graph)
        nodes = [node[0] for node in sorted(degrees, key=lambda x: x[1], reverse=True)]
        first_index = 0
        while len(nodes) > 0:
            neighbors = list(graph.neighbors(nodes[first_index]))
            clique.add(nodes[first_index])
            nodes = list(filter(lambda x: x in neighbors, nodes))
        return clique

    @staticmethod
    def largest_first_randomized(graph: nx.Graph, n_iterations: int = 50,
                                 k_first: int = 5, **kwargs):
        best_clique = None
        best_clique_size = 0
        for _ in range(n_iterations):
            clique = set()
            nodes = [node[0] for node in sorted(nx.degree(graph), key=lambda x: x[1], reverse=True)]
            while len(nodes) > 0:
                random_index = np.random.randint(0, min(k_first, len(nodes)))
                neighbors = list(graph.neighbors(nodes[random_index]))
                clique.add(nodes[random_index])
                nodes = list(filter(lambda x: x in neighbors, nodes))
            if len(clique) > best_clique_size:
                best_clique = clique
                best_clique_size = len(clique)
        return best_clique


def test_max_clique_heuristic():
    benches = {**EASY, **MEDIUM, **HARD}
    for bench in benches:
        G = read_graph_file(bench, verbose=False)
        heuristic = HeuristicMaxClique(G)
        found_clique = heuristic.run()
        print(f'Bench: {bench}')
        print(f'Found clique: {sum(found_clique)} True clique: {benches[bench]}')
