import cplex
import numpy as np
from math import isclose

import utils
from problem import ProblemHandler


class BranchAndBound:

    def __init__(self, initial_obj_value: float, initial_solution: list,
                 num_of_nodes: int, abs_tol: float = 1e-4):
        """
        :param initial_obj_value: initial value of the objective function
        :param num_of_nodes: the number of nodes in the graph
        :param abs_tol: the value of absolute tolerance
        """
        self.call_counter = 0
        self.recursion_depth = 0
        self.max_recursion_depth = 0
        self.best_obj_value = initial_obj_value
        self.best_solution = initial_solution
        self.num_of_nodes = num_of_nodes
        self.node_indexes = list(range(num_of_nodes))
        self.constrained_vars = np.zeros(num_of_nodes, dtype=np.bool)
        self.constrained_count = np.array([self.num_of_nodes] * self.num_of_nodes, dtype=np.int)
        self.constraint_size = 0
        self.abs_tol = abs_tol

    @utils.timer
    def timed_run(self, problem: ProblemHandler):
        self.run(problem)
        return

    def run(self, problem: ProblemHandler):
        # PERFORMANCE CHECK: RATHER OK
        self.call_counter += 1
        try:
            current_obj_value = problem.solve_problem()
        except cplex.exceptions.CplexSolverError:
            return
        if int(current_obj_value + self.abs_tol) <= self.best_obj_value:
            return
        current_solution = problem.get_solution()
        if self.call_counter % 1000 == 0:
            print(f'call_counter: {self.call_counter}', f'max depth {self.max_recursion_depth}', '\ncurrent solution:',
                  current_obj_value) # , current_solution)
            print('Constraint size:', self.constraint_size)

        if self.is_all_integer(current_solution, abs_tol=self.abs_tol):
            clique_nodes = utils.to_node_indexes(current_solution, abs_tol=self.abs_tol)
            is_clique = utils.is_clique(problem.graph, clique_nodes)
            print('IS CLIQUE?:', is_clique)
            if not is_clique:
                return
            print('NEW BEST SOLUTION', current_obj_value) #, current_solution)
            print('NEW BEST SOLUTION', [f'x{x}' for x in clique_nodes])
            print('Constraint size:', self.constraint_size)
            self.best_solution = current_solution
            self.best_obj_value = current_obj_value
            return

        branching_var_index = self.select_branching_var(current_solution)
        if not branching_var_index:
            return
        branching_var = f'x{branching_var_index + 1}'
        for branch_value in [1, 0]:
            constraint_name = f'C{self.call_counter}_branch{branch_value}_{branching_var}'
            problem.add_integer_constraint(variable=branching_var,
                                           constraint_name=constraint_name,
                                           right_hand_side=branch_value)
            self.constrained_vars[branching_var_index] = 1
            self.constraint_size += 1
            self.recursion_depth += 1
            self.max_recursion_depth = max(self.recursion_depth, self.max_recursion_depth)
            self.run(problem)
            problem.remove_constraint(constraint_name)
            self.constrained_vars[branching_var_index] = 0
            self.constraint_size -= 1
            self.recursion_depth -= 1
        if self.constrained_count[branching_var_index] > 0:
            self.constrained_count[branching_var_index] -= 1
        return

    def select_branching_var(self, solution_values) -> int:
        selected_var_index = None
        min_diff_to_int = 100000
        if np.random.randint(0, 20) == 0:
            _sum = self.constrained_count.sum()
            if _sum > 0:
                random_i = np.random.choice(self.node_indexes, p=self.constrained_count / _sum)
                if self.constrained_vars[random_i] != 1 and self.constrained_count[random_i] > 0:
                    selected_var_index = random_i
                    return selected_var_index
        for _index, value in enumerate(solution_values):
            if self.constrained_vars[_index] != 1:
                diff_to_int = abs(1 - value)
                if diff_to_int <= min_diff_to_int:
                    min_diff_to_int = diff_to_int
                    selected_var_index = _index
        return selected_var_index

    @staticmethod
    def is_all_integer(variables, abs_tol=0.001):
        # PERFORMANCE CHECK: OK
        for var in variables:
            if not BranchAndBound.is_integer(var, abs_tol=abs_tol):
                return False
        return True

    @staticmethod
    def is_integer(var, abs_tol=0.001):
        # PERFORMANCE CHECK: OK
        return isclose(var, 0, abs_tol=abs_tol) or isclose(var, 1, abs_tol=abs_tol)
