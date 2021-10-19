import numpy as np

import utils
from run_test import *
from problem import ProblemHandler
from branch_and_bound import BranchAndBound
from heuristic import HeuristicMaxClique

if __name__ == '__main__':
    # args = utils.main_arg_parser()
    # filepath = args.filepath  # 'benchmarks/DIMACS_all_ascii/C125.9.clq'
    benches = list(MEDIUM.items())
    i = int(input())
    filepath = benches[i][0]

    G = utils.read_graph_file(filepath)
    problem_handler = ProblemHandler(graph=G)
    problem_handler.design_problem()
    heuristic = HeuristicMaxClique(G)
    heuristic_clique = heuristic.run()
    heuristic_clique_size = int(sum(heuristic_clique))
    bnb_algorithm = BranchAndBound(initial_solution=heuristic_clique,
                                   initial_obj_value=heuristic_clique_size,
                                   num_of_nodes=G.number_of_nodes(), abs_tol=1e-3)

    print(f'Problem constructed for {filepath}!')
    print('TRUE CLIQUE SIZE:', benches[i][1])
    print('HEURISTIC CLIQUE:', utils.to_node_indexes(heuristic_clique))
    print('HEURISTIC CLIQUE SIZE:', heuristic_clique_size)
    print('Is clique?', utils.is_clique(G, utils.to_node_indexes(heuristic_clique)))

    time_lst = bnb_algorithm.timed_run(problem_handler)
    clique_nodes = utils.to_node_indexes(bnb_algorithm.best_solution)

    print('*' * 50)
    print('BEST BNB OBJ VALUE', bnb_algorithm.best_obj_value)
    print('BEST BNB SOLUTION', [f'x{x}' for x in clique_nodes])
    print(f'CALL COUNT {bnb_algorithm.call_counter} MAX DEPTH {bnb_algorithm.max_recursion_depth}')
    print('Is clique?', utils.is_clique(G, clique_nodes))
    minutes, seconds = divmod(np.mean(time_lst), 60)
    print(f'Execution time: {minutes:.0f}min {seconds:.1f}sec')
    print(f'for {G.number_of_nodes()} nodes and {G.number_of_edges()} edges\n')
