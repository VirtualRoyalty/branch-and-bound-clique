import cplex
import numpy as np
import networkx as nx
import utils


class ProblemHandler:
    constructed_problem: cplex.Cplex
    STRATEGIES = [
        nx.coloring.strategy_largest_first,
        nx.coloring.strategy_random_sequential,
        nx.coloring.strategy_independent_set,
        nx.coloring.strategy_connected_sequential_bfs,
        nx.coloring.strategy_connected_sequential_dfs,
        nx.coloring.strategy_saturation_largest_first
    ]

    def __init__(self, graph: nx.Graph, is_integer: bool = False):
        self.constructed_problem = None
        self.graph = graph
        self.is_integer = is_integer
        return

    def solve_problem(self) -> float:
        if self.constructed_problem:
            self.constructed_problem.solve()
            return self.constructed_problem.solution.get_objective_value()
        else:
            raise "Problem is not constructed yet"

    def get_solution(self) -> dict:
        if self.constructed_problem:
            return self.constructed_problem.solution.get_values()
        else:
            raise "Problem is not constructed yet"

    def add_integer_constraint(self, variable, constraint_name, right_hand_side=1.0):
        constraint = [[variable], [1.0]]
        if self.constructed_problem:
            self.constructed_problem.linear_constraints.add(lin_expr=[constraint],
                                                            senses=['E'],
                                                            rhs=[right_hand_side],
                                                            names=[constraint_name])
            return
        else:
            raise "Problem is not constructed yet"

    def remove_constraint(self, constraint_name):
        if self.constructed_problem:
            self.constructed_problem.linear_constraints.delete(constraint_name)
            return
        else:
            raise "Problem is not constructed yet"

    def design_problem(self):
        # specify numeric type for ILP/LP problem
        one = 1 if self.is_integer else 1.0
        zero = 0 if self.is_integer else 0.0

        # get not connected edges and list of independent sets
        not_connected = self.get_complement_edges(self.graph)
        independent_sets = self.get_independent_sets(self.graph, strategies=self.STRATEGIES)

        # define num of decision vars by num of nodes
        # and num of constraints as num of not connected edges + num of found ind sets
        nodes = sorted(self.graph.nodes())
        n_vars = self.graph.number_of_nodes()
        n_constraints = len(not_connected) + len(independent_sets)

        # define upper and lower bounds for vars
        upper_bounds = [one] * n_vars
        lower_bounds = [zero] * n_vars
        # define objective x_1 + x_2 + ... + x_n -> max
        obj = [one] * n_vars
        # define var and constraint names
        var_names = [f'x{i}' for i in nodes]
        constraint_names = [f'c{i + 1}' for i in range(n_constraints)]
        # constraint type L is less than, i. e. x_i + x_j <= 1
        constraint_senses = ['L'] * n_constraints
        right_hand_side = [one] * n_constraints

        # initialize cplex solver
        problem = cplex.Cplex()
        # add vars, obj and bounds
        problem.variables.add(obj=obj, names=var_names, ub=upper_bounds, lb=lower_bounds)

        # collect constraints and var types
        constraints = []
        for ind_set in independent_sets:
            constraints.append([[f'x{i}' for i in ind_set], [1.0] * len(ind_set)])
        for i, j in not_connected:
            constraints.append([[f'x{i}', f'x{j}'], [1.0, 1.0]])
        _type = problem.variables.type.binary if self.is_integer else problem.variables.type.continuous
        for node in nodes:
            problem.variables.set_types(f'x{node}', _type)

        # add constraints and var types
        problem.linear_constraints.add(lin_expr=constraints,
                                       senses=constraint_senses,
                                       rhs=right_hand_side,
                                       names=constraint_names)
        # set objective func as maximization problem
        problem.objective.set_sense(problem.objective.sense.maximize)
        self.constructed_problem = problem
        return

    @staticmethod
    def get_complement_edges(graph: nx.Graph) -> list:
        complement_g = nx.complement(graph)
        adj_matrix = nx.adjacency_matrix(complement_g).todense()
        adj_matrix = np.triu(adj_matrix, k=1)
        pairs = np.where(adj_matrix == 1)
        complement_edges = list(zip(pairs[0] + 1, pairs[1] + 1))
        # print(len(complement_edges))
        return complement_edges

    # TODO: deprecate this func
    @staticmethod
    def get_independent_sets_deprecated(graph: nx.Graph, strategies: list, min_set_size: int = 3) -> list:
        independent_sets = []
        for strategy in strategies:
            vertex_color_dict = nx.coloring.greedy_color(graph, strategy=strategy)
            unique_colors = set(color for node, color in vertex_color_dict.items())
            for color in unique_colors:
                color_set = tuple(sorted([int(key) for key, value in vertex_color_dict.items() if value == color]))
                if len(color_set) >= min_set_size:
                    independent_sets.append(color_set)
        independent_sets = list(set(independent_sets))
        return independent_sets

    @staticmethod
    def get_independent_sets(graph: nx.Graph, strategies: list, min_set_size: int = 3) -> list:
        independent_sets = set()
        for strategy in strategies:
            vertex_color_dct = nx.coloring.greedy_color(graph, strategy=strategy)
            unique_colors = set()
            color_set_dct = dict()

            for node, color in vertex_color_dct.items():
                unique_colors.add(color)
                if color in color_set_dct:
                    color_set_dct[color].append(node)
                else:
                    color_set_dct[color] = [node]

            for color, color_set in color_set_dct.items():
                if len(color_set) >= min_set_size:
                    sorted_color_set = tuple(sorted(color_set))
                    independent_sets.add(sorted_color_set)
        independent_sets = list(independent_sets)
        return independent_sets

# @utils.timer
# def solve_problem(some_problem: cplex.Cplex):
#     some_problem.solve()
