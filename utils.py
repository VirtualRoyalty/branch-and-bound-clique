import time
import math
import functools

import networkx
import networkx as nx
import argparse


def to_node_indexes(solution: list, abs_tol: float = 1e-5) -> list:
    return [var_index + 1 for var_index, var in enumerate(solution)
            if math.isclose(var, 1, abs_tol=abs_tol)]


def is_clique(graph: nx.Graph, nodes: list) -> bool:
    subgraph: nx.Graph = graph.subgraph(nodes)
    num_of_nodes = subgraph.number_of_nodes()
    num_of_edges = subgraph.number_of_edges()
    num_of_edges_complete = int(num_of_nodes * (num_of_nodes - 1) / 2)
    if num_of_edges == num_of_edges_complete:
        return True
    return False


def read_graph_file(file_path: str, verbose: bool = True) -> nx.Graph:
    edges = []
    file = open(file_path, 'r')
    for line in file:
        if line.startswith('c'):  # graph description
            if verbose:
                print(*line.split()[1:])
        elif line.startswith('p'):
            _, _, n_nodes, n_edges = line.split()
            if verbose:
                print(f'Nodes:  {n_nodes} Edges: {n_edges}')
        elif line.startswith('e'):
            _, node_i, node_j = line.split()
            edges.append((int(node_i), int(node_j)))
        else:
            continue
    g = nx.Graph(edges)
    assert int(n_nodes) == g.number_of_nodes()
    assert int(n_edges) == g.number_of_edges()
    return g


class TimeoutException(Exception):
    def __init__(self, best_clique_size: int, msg: str = 'TIME OUT!'):
        self.msg = msg
        self.best_clique_size = best_clique_size


def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = time.perf_counter()
        _ = func(*args, **kwargs)
        toc = time.perf_counter()
        elapsed_time = toc - tic
        return elapsed_time

    return wrapper_timer


def main_arg_parser():
    parser = argparse.ArgumentParser(description='Solve maximum clique problem by CPLEX solver')
    parser.add_argument('--filepath', type=str, required=True,
                        help='Path to DIMACS-format file')
    parser.add_argument('--abs_tol', type=float, required=False,
                        default=1e-5, help='absolute tolerance value for comparative operations')
    parser.add_argument('--verbose', type=bool, default=False,
                        help='Whether to stream solver logs')
    return parser.parse_args()
