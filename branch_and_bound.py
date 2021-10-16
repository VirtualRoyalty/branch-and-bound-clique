import numpy as np
import networkx as nx
from math import isclose

import utils
from problem import ProblemHandler


class BranchAndBound:

    def __init__(self):
        self.recursion_counter = 0
        self.best_solution = None
        self.best_obj_value = None
        self.abs_tol = 1e-5
        pass

    def run(self, problem_handler: ProblemHandler):
        self.recursion_counter += 1
        current_obj_value = problem_handler.solve_problem()
        if current_obj_value + self.abs_tol <= self.best_obj_value:
            return
        current_solution = problem_handler.get_solution()
        if is_all_integer(current_solution.values(), abs_tol=self.abs_tol):
            self.best_solution = current_solution
            self.best_obj_value = current_obj_value

        branching_var = self.choose_branching_variable(current_solution.values())
        for branch in [0.0, 1.0]:
            constraint_name = f'C{self.recursion_counter}_branch{branch}'
            problem_handler.add_integer_constraint(variable=branching_var,
                                                   constraint_name=constraint_name)
            self.run(problem_handler)
            problem_handler.remove_constraint(constraint_name)

    def choose_branching_variable(self, solution_values):
        # TODO: write branching variable strategies
        return 1


def is_all_integer(variables, abs_tol=0.001):
    for var in variables:
        if not is_integer(var, abs_tol=abs_tol):
            return False
    return True


def is_integer(var, abs_tol=0.001):
    return isclose(var, 0, abs_tol=abs_tol) or isclose(var, 1, abs_tol=abs_tol)


# if __name__ == '__main__':

    # args = utils.main_arg_parser()
    # filepath = args.filepath  # 'benchmarks/DIMACS_all_ascii/C125.9.clq'
    # G = utils.read_graph_file(filepath)
    # designer = ProblemHandler(graph=G)
    # designer.design_problem()
    # max_clique_problem = designer.constructed_problem
    # if not args.verbose:
    #     max_clique_problem.set_log_stream(None)
    #     max_clique_problem.set_results_stream(None)
    #     max_clique_problem.set_warning_stream(None)
    # print(f'Problem constructed for {filepath}!')
    #
    # # solve problem
    # print('Start solving...')
    # time_lst = solve_problem(max_clique_problem)
    # solution = max_clique_problem.solution.get_values()
    # obj_value = max_clique_problem.solution.get_objective_value()
    # print(f'Found max clique size (obj func value): {obj_value}')
    # print(*[f'x{i}={value:.2f}' for i, value in enumerate(solution) if value != 0])
    #
    # mean_time = np.mean(time_lst)
    # mins, secs = divmod(mean_time, 60)
    # print(f'Execution time: {mins:.0f}min {secs:.1f}sec')
    # print(f'for {G.number_of_nodes()} nodes and {G.number_of_edges()} edges\n')