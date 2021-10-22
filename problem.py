import cplex
import numpy as np
import networkx as nx


class ProblemHandler:
    problem: cplex.Cplex
    STRATEGIES = [
        nx.coloring.strategy_largest_first,
        nx.coloring.strategy_random_sequential,
        nx.coloring.strategy_independent_set,
        nx.coloring.strategy_connected_sequential_bfs,
        nx.coloring.strategy_saturation_largest_first,
    ]

    def __init__(self, graph: nx.Graph, is_integer: bool = False, verbose: bool = False):
        """
        :param graph: the graph for the max clique problem
        :param is_integer: if True then LP mode else ILP mode for cplex solver
        """
        self.problem = None
        self.graph = graph
        self.is_integer = is_integer
        self.verbose = verbose
        return

    def solve_problem(self) -> float:
        if self.problem:
            self.problem.solve()
            return self.problem.solution.get_objective_value()
        else:
            raise "Problem is not constructed yet"

    def get_solution(self) -> list:
        if self.problem:
            return self.problem.solution.get_values()
        else:
            raise "Problem is not constructed yet"

    def add_integer_constraint(self, var_name: str, constraint_name: str,
                               rhs: float = 1.0):
        constraint = [[var_name], [1.0]]
        if self.problem:
            self.problem.linear_constraints.add(lin_expr=[constraint], senses=['E'],
                                                rhs=[rhs], names=[constraint_name])
            return
        else:
            raise "Problem is not constructed yet"

    def remove_constraint(self, constraint_name):
        if self.problem:
            self.problem.linear_constraints.delete(constraint_name)
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
        for node_i, node_j in not_connected:
            constraints.append([[f'x{node_i}', f'x{node_j}'], [1.0, 1.0]])
        _type = problem.variables.type.binary if self.is_integer else problem.variables.type.continuous
        for node in nodes:
            problem.variables.set_types(f'x{node}', _type)
        # add constraints and var types
        problem.linear_constraints.add(lin_expr=constraints, senses=constraint_senses,
                                       rhs=right_hand_side, names=constraint_names)
        # set objective func as maximization problem
        problem.objective.set_sense(problem.objective.sense.maximize)
        self.problem = problem
        self.set_verbosity()
        return

    def set_verbosity(self):
        if not self.verbose:
            self.problem.set_log_stream(None)
            self.problem.set_results_stream(None)
            self.problem.set_warning_stream(None)
            self.problem.set_error_stream(None)

    @staticmethod
    def get_complement_edges(graph: nx.Graph) -> list:
        complement_g = nx.complement(graph)
        adj_matrix = nx.adjacency_matrix(complement_g).todense()
        adj_matrix = np.triu(adj_matrix, k=1)
        pairs = np.where(adj_matrix == 1)
        complement_edges = list(zip(pairs[0] + 1, pairs[1] + 1))
        return complement_edges

    @staticmethod
    def get_independent_sets(graph: nx.Graph, strategies: list,
                             n_iter: int = 50, min_set_size: int = 3) -> list:
        independent_sets = set()
        for strategy in strategies:
            if strategy == nx.coloring.strategy_random_sequential:
                _n_iter = n_iter
            else:
                _n_iter = 1
            for _ in range(_n_iter):
                coloring_dct = nx.coloring.greedy_color(graph, strategy=strategy)
                color2nodes = dict()
                for node, color in coloring_dct.items():
                    if color not in color2nodes:
                        color2nodes[color] = []
                    color2nodes[color].append(node)
                for color, colored_nodes in color2nodes.items():
                    if len(colored_nodes) >= min_set_size:
                        colored_nodes = tuple(sorted(colored_nodes))
                        independent_sets.add(colored_nodes)
        independent_sets = list(independent_sets)
        return independent_sets
