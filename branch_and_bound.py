import time
import numpy as np
from math import isclose

import utils
from problem import ProblemHandler


class BranchAndBound:

    def __init__(self, best_obj_value: float, num_of_nodes: int):
        self.call_counter = 0
        self.best_solution = None
        self.best_obj_value = best_obj_value
        self.num_of_nodes = num_of_nodes
        self.node_indexes = list(range(num_of_nodes))
        self.constrained_vars = np.zeros(num_of_nodes, dtype=np.bool)
        # self.constrained_count = np.zeros(num_of_nodes, dtype=np.int)
        self.constrained_count = np.array([self.num_of_nodes]*self.num_of_nodes, dtype=np.int)
        self.constraint_size = 0
        self.abs_tol = 0.0001
        pass

    def run(self, problem: ProblemHandler):
        # PERFORMANCE CHECK: RATHER OK
        self.call_counter += 1
        try:
            current_obj_value = problem.solve_problem()
        except Exception as error:
            # print(error)
            return
        if int(current_obj_value + self.abs_tol) <= self.best_obj_value:
            return
        current_solution = problem.get_solution()
        if self.call_counter % 1000 == 0:
            print(f'call_counter: {self.call_counter}')
            print('current solution:', current_obj_value, current_solution)
            print('Constraint size:', self.constraint_size)
            # print('Constraint count:', self.constrained_count)
        # print('Solution:', current_solution)
        if is_all_integer(current_solution, abs_tol=self.abs_tol):
            print('NEW BEST SOLUTION', current_obj_value, current_solution)
            print('Constraint size:', self.constraint_size)
            self.best_solution = current_solution
            self.best_obj_value = current_obj_value
            return

        branching_var_index = self.choose_branching_variable(current_solution)
        if not branching_var_index:
            return
        # print('Constraint set:', self.constraint_vars_set)
        branching_var = f'x{branching_var_index+1}'
        if abs(1.0 - current_solution[branching_var_index]) < abs(current_solution[branching_var_index]):
            branch_order = [1, 0]
        else:
            branch_order = [0, 1]
        for branch_value in branch_order:
            constraint_name = f'C{self.call_counter}_branch{branch_value}_{branching_var}'
            # print('Added:', constraint_name)
            problem.add_integer_constraint(variable=branching_var,
                                           constraint_name=constraint_name,
                                           right_hand_side=branch_value)
            self.constrained_vars[branching_var_index] = 1
            self.constraint_size += 1
            # print(problem_handler.constructed_problem.linear_constraints.get_names()[-10:])
            self.run(problem)
            problem.remove_constraint(constraint_name)
            self.constrained_vars[branching_var_index] = 0
            self.constraint_size -= 1
            # print('Deleted:', constraint_name)
        if self.constrained_count[branching_var_index] > 0:
            self.constrained_count[branching_var_index] -= 1
        return

    def choose_branching_variable(self, solution_values) -> int:
        # PERFORMANCE CHECK: NOT OK
        branching_var_index = None
        min_diff_to_int = 1000
        for i, value in enumerate(solution_values):
            if np.random.randint(0, self.num_of_nodes//2) == 1:
                _sum = self.constrained_count.sum()
                if _sum > 0:
                    random_i = np.random.choice(self.node_indexes,
                                                p=self.constrained_count / _sum)
                    if self.constrained_vars[random_i] != 1 and self.constrained_count[random_i] > 0:
                        branching_var_index = random_i
                        return branching_var_index
            diff_to_int = min(abs(1 - value), abs(value))
            if diff_to_int <= min_diff_to_int:
                if self.constrained_vars[i] != 1:
                    min_diff_to_int = diff_to_int
                    branching_var_index = i
        return branching_var_index


def is_all_integer(variables, abs_tol=0.001):
    # PERFORMANCE CHECK: OK
    for var in variables:
        if not is_integer(var, abs_tol=abs_tol):
            return False
    return True


def is_integer(var, abs_tol=0.001):
    # PERFORMANCE CHECK: OK
    return isclose(var, 0, abs_tol=abs_tol) or isclose(var, 1, abs_tol=abs_tol)


if __name__ == '__main__':
    args = utils.main_arg_parser()
    filepath = args.filepath  # 'benchmarks/DIMACS_all_ascii/C125.9.clq'
    G = utils.read_graph_file(filepath)
    problem_handler = ProblemHandler(graph=G)
    problem_handler.design_problem()
    max_clique_problem = problem_handler.constructed_problem
    if not args.verbose:
        max_clique_problem.set_log_stream(None)
        max_clique_problem.set_results_stream(None)
        max_clique_problem.set_warning_stream(None)
        max_clique_problem.set_error_stream(None)
    print(f'Problem constructed for {filepath}!')
    bnb_algorithm = BranchAndBound(best_obj_value=4, num_of_nodes=problem_handler.graph.number_of_nodes())
    tic = time.perf_counter()
    bnb_algorithm.run(problem_handler)
    toc = time.perf_counter()
    time_lst = [toc - tic]
    print('BEST BNB OBJ VALUE', bnb_algorithm.best_obj_value)
    print('BEST BNB SOLUTION', bnb_algorithm.best_solution)

    # # solve problem
    # print('Start solving...')
    # time_lst = solve_problem(max_clique_problem)
    # solution = max_clique_problem.solution.get_values()
    # obj_value = max_clique_problem.solution.get_objective_value()
    # print(f'Found max clique size (obj func value): {obj_value}')
    # print(*[f'x{i}={value:.2f}' for i, value in enumerate(solution) if value != 0])
    #
    mean_time = np.mean(time_lst)
    minutes, seconds = divmod(mean_time, 60)
    print(f'Execution time: {minutes:.0f}min {seconds:.1f}sec')
    print(f'for {G.number_of_nodes()} nodes and {G.number_of_edges()} edges\n')
