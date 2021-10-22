import cplex
import time
import numpy as np
from math import isclose

import utils
from problem import ProblemHandler


class BranchAndBound:

    def __init__(self, problem: ProblemHandler, initial_obj_value: float, initial_solution: list,
                 abs_tol: float = 1e-4, time_limit: int = None):
        self.call_counter = 0
        self.recursion_depth = 0
        self.max_recursion_depth = 0
        self.problem = problem
        self.best_obj_value = initial_obj_value
        self.best_solution = initial_solution
        self.num_of_nodes = problem.graph.number_of_nodes()
        self.constrained_vars = np.zeros(self.num_of_nodes, dtype=np.bool)
        self.constraint_size = 0
        self.abs_tol = abs_tol
        self.start_time = None
        self.time_limit = time_limit

    @utils.timer
    def timed_run(self):
        if self.time_limit:
            self.start_time = time.perf_counter()
        self.run()
        return

    def run(self):
        self.call_counter += 1
        try:
            current_obj_value = self.problem.solve_problem()
        except cplex.exceptions.CplexSolverError as error:
            print(error)
            return
        if int(current_obj_value + self.abs_tol) <= self.best_obj_value:
            return
        current_solution = self.problem.get_solution()
        if self.is_all_integer(current_solution, abs_tol=self.abs_tol):
            clique_nodes = utils.to_node_indexes(current_solution, abs_tol=self.abs_tol)
            is_clique = utils.is_clique(self.problem.graph, clique_nodes)
            if not is_clique:
                return
            print(f'Found new best: {round(current_obj_value)}')
            self.best_solution = current_solution
            self.best_obj_value = round(current_obj_value)
            return

        if self.time_limit:
            elapsed_time = time.perf_counter() - self.start_time
            if elapsed_time > self.time_limit:
                raise utils.TimeoutException(best_clique_size=self.best_obj_value,
                                             msg=f'TIMEOUT: >{round(elapsed_time)}s elapsed')

        branching_var_index = self.select_branching_var(current_solution)
        if branching_var_index is None:
            return
        branching_var_name = f'x{branching_var_index + 1}'
        rounded_value = round(current_solution[branching_var_index])
        for branch_value in [rounded_value, 1 - round(rounded_value)]:
            constraint_name = f'C{self.call_counter}_branch{branch_value}_{branching_var_name}'
            self.problem.add_integer_constraint(var_name=branching_var_name, rhs=branch_value,
                                                constraint_name=constraint_name)
            self.constrained_vars[branching_var_index] = 1
            self.constraint_size += 1
            self.recursion_depth += 1
            self.max_recursion_depth = max(self.recursion_depth, self.max_recursion_depth)
            self.run()
            self.problem.remove_constraint(constraint_name)
            self.constrained_vars[branching_var_index] = 0
            self.constraint_size -= 1
            self.recursion_depth -= 1
        return

    def select_branching_var(self, solution: list) -> int:
        selected_var_index = None
        min_diff_to_int = 2
        for _index, value in enumerate(solution):
            if self.constrained_vars[_index] != 1:
                diff_to_int = abs(1 - value)
                if diff_to_int <= min_diff_to_int:
                    min_diff_to_int = diff_to_int
                    selected_var_index = _index
        return selected_var_index

    @staticmethod
    def is_all_integer(variables: list, abs_tol: float = 1e-4) -> bool:
        for var in variables:
            if not BranchAndBound.is_integer(var, abs_tol=abs_tol):
                return False
        return True

    @staticmethod
    def is_integer(var: float, abs_tol: float = 1e-4) -> bool:
        return isclose(var, 0, abs_tol=abs_tol) or isclose(var, 1, abs_tol=abs_tol)
