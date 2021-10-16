import numpy as np
import networkx as nx
from math import isclose

import utils
from problem import ProblemHandler


def branch_and_bound(problem_handler):
    problem_handler.solve()

    return


def is_all_integer(variables):
    for var in variables:
        if not is_integer(var):
            return False
    return True


def is_integer(var, abs_tol=0.001):
    return isclose(var, 0, abs_tol=abs_tol) or isclose(var, 1, abs_tol=abs_tol)
    # if isclose(var, 0, abs_tol=abs_tol):
    #     return 0
    # elif isclose(var, 1, abs_tol=abs_tol):
    #     return 1
    # else:
    #     return -1


if __name__ == '__main__':

    args = utils.main_arg_parser()
    filepath = args.filepath  # 'benchmarks/DIMACS_all_ascii/C125.9.clq'
    G = utils.read_graph_file(filepath)
    designer = ProblemHandler(graph=G)
    designer.design_problem()
    max_clique_problem = designer.constructed_problem
    if not args.verbose:
        max_clique_problem.set_log_stream(None)
        max_clique_problem.set_results_stream(None)
        max_clique_problem.set_warning_stream(None)
    print(f'Problem constructed for {filepath}!')

    # solve problem
    print('Start solving...')
    time_lst = solve_problem(max_clique_problem)
    solution = max_clique_problem.solution.get_values()
    obj_value = max_clique_problem.solution.get_objective_value()
    print(f'Found max clique size (obj func value): {obj_value}')
    print(*[f'x{i}={value:.2f}' for i, value in enumerate(solution) if value != 0])

    mean_time = np.mean(time_lst)
    mins, secs = divmod(mean_time, 60)
    print(f'Execution time: {mins:.0f}min {secs:.1f}sec')
    print(f'for {G.number_of_nodes()} nodes and {G.number_of_edges()} edges\n')