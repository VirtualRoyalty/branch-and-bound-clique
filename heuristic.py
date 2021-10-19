import numpy as np
import networkx as nx
from run_test import *
from utils import *


class HeuristicMaxClique:

    def __init__(self, graph: nx.Graph):
        self.graph = graph
        self.strategies = [self.largest_first,
                           self.largest_first_randomized]

    def run(self):
        found_clique = 0
        best_colors = None
        for strategy in self.strategies:
            colors = strategy(self.graph)
            if found_clique < len(colors):
                found_clique = len(colors)
                best_colors = colors
        return [1.0 if i + 1 in best_colors else 0.0
                for i in range(self.graph.number_of_nodes())]

    @staticmethod
    def largest_first(graph: nx.Graph):
        colors = set()
        nodes = [node[0] for node in sorted(nx.degree(graph), key=lambda x: x[1], reverse=True)]
        first_index = 0
        while len(nodes) > 0:
            neighbors = list(graph.neighbors(nodes[first_index]))
            colors.add(nodes[first_index])
            nodes.remove(nodes[first_index])
            nodes = list(filter(lambda x: x in neighbors, nodes))
        return colors

    @staticmethod
    def largest_first_randomized(graph: nx.Graph, n_iterations: int = 50,
                                 k_first: int = 5):
        best_colors = None
        best_clique_size = 0
        for _ in range(n_iterations):
            colors = set()
            nodes = [node[0] for node in sorted(nx.degree(graph), key=lambda x: x[1], reverse=True)]
            while len(nodes) > 0:
                random_index = np.random.randint(0, min(k_first, len(nodes)))
                neighbors = list(graph.neighbors(nodes[random_index]))
                colors.add(nodes[random_index])
                nodes.remove(nodes[random_index])
                nodes = list(filter(lambda x: x in neighbors, nodes))
            if len(colors) > best_clique_size:
                best_colors = colors
                best_clique_size = len(colors)
        return best_colors

    def smallest_last(self):
        return


def test_greedy():
    benches = {**EASY, **MEDIUM, **HARD}
    for bench in benches:
        G = read_graph_file(bench, verbose=False)
        heuristic = HeuristicMaxClique(G)
        found_clique = heuristic.run()
        print(f'Bench: {bench}')
        print(f'Found clique: {len(found_clique)} True clique: {benches[bench]}')
