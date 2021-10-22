import pandas as pd

from main import *
from branch_and_bound import *
from utils import *
from heuristic import *

EASY = {
    'benchmarks/DIMACS_all_ascii/johnson8-2-4.clq': 4,
    'benchmarks/DIMACS_all_ascii/johnson16-2-4.clq': 8,
    'benchmarks/DIMACS_all_ascii/MANN_a9.clq': 16,
    'benchmarks/DIMACS_all_ascii/keller4.clq': 11,
    'benchmarks/DIMACS_all_ascii/c-fat200-1.clq': None,
    'benchmarks/DIMACS_all_ascii/c-fat500-1.clq': None,
    'benchmarks/DIMACS_all_ascii/c-fat500-10.clq': None,
    'benchmarks/DIMACS_all_ascii/c-fat200-2.clq': None,
    'benchmarks/DIMACS_all_ascii/hamming8-4.clq': 16,
}

MEDIUM = {
    'benchmarks/DIMACS_all_ascii/gen200_p0.9_55.clq': 55,
    'benchmarks/DIMACS_all_ascii/gen200_p0.9_44.clq': 44,
    'benchmarks/DIMACS_all_ascii/C125.9.clq': 34,
    'benchmarks/DIMACS_all_ascii/brock200_2.clq': 12,
    'benchmarks/DIMACS_all_ascii/brock200_3.clq': 15,
    'benchmarks/DIMACS_all_ascii/brock200_4.clq': 17,
    'benchmarks/DIMACS_all_ascii/brock200_1.clq': 21,
    'benchmarks/DIMACS_all_ascii/p_hat1000-1.clq': 10,
    # 'benchmarks/DIMACS_all_ascii/san1000.clq': 15,
}

HARD = {
    'benchmarks/DIMACS_all_ascii/brock400_1.clq': 27,
    'benchmarks/DIMACS_all_ascii/brock400_2.clq': 29,
    'benchmarks/DIMACS_all_ascii/brock400_3.clq': 31,
    'benchmarks/DIMACS_all_ascii/brock400_4.clq': 33,
    'benchmarks/DIMACS_all_ascii/MANN_a27.clq': 126,
    'benchmarks/DIMACS_all_ascii/MANN_a45.clq': 345,
    'benchmarks/DIMACS_all_ascii/sanr400_0.7.clq': 21,
    # 'benchmarks/DIMACS_all_ascii/sanr400_0.9.clq': 42,
    'benchmarks/DIMACS_all_ascii/p_hat1000-2.clq': 46,
    'benchmarks/DIMACS_all_ascii/p_hat500-3.clq': 50,
    'benchmarks/DIMACS_all_ascii/p_hat1500-1.clq': 12,
    'benchmarks/DIMACS_all_ascii/p_hat300-3.clq': 36,
}


def run_test(benchmark: str, abs_tol: float = 1e-4, time_limit: int = None):
    print(f'{benchmark} started...')
    graph = read_graph_file(benchmark, verbose=False)
    problem_handler = ProblemHandler(graph=graph)
    problem_handler.design_problem()
    print('Problem constructed!')
    heuristic = HeuristicMaxClique(graph)
    heuristic_clique = heuristic.run()
    heuristic_clique_size = int(sum(heuristic_clique))
    print(f'Found heuristic solution! ({heuristic_clique_size})')
    bnb_algorithm = BranchAndBound(problem=problem_handler,
                                   initial_solution=heuristic_clique, time_limit=time_limit,
                                   initial_obj_value=heuristic_clique_size, abs_tol=abs_tol)
    exec_time = bnb_algorithm.timed_run()
    clique_nodes = to_node_indexes(bnb_algorithm.best_solution)
    _minutes, _seconds = divmod(exec_time, 60)
    _result = dict(benchmark=benchmark.split('/')[-1],
                   heuristic_clique_size=heuristic_clique_size,
                   bnb_clique_size=bnb_algorithm.best_obj_value,
                   is_bnb_solution_clique=is_clique(graph, clique_nodes),
                   bnb_exec_time=f'{_minutes:.0f}min {_seconds:.1f}sec',
                   bnb_exec_time_seconds=exec_time,
                   bnb_call_count=bnb_algorithm.call_counter,
                   bnb_max_recursion_depth=bnb_algorithm.max_recursion_depth,
                   )
    return _result


def run_tests(benchmarks: list, time_limit: int = None, abs_tol: float = 1e-4,
              out_folder: str = 'results/', suffix: str = ''):
    results = []
    for filepath in benchmarks:
        try:
            result_dct = run_test(filepath, abs_tol=abs_tol, time_limit=time_limit)
        except TimeoutException as timeout:
            print(filepath, timeout.msg)
            results.append(dict(benchmark=filepath.split('/')[-1],
                                bnb_exec_time=timeout.msg,
                                bnb_clique_size=timeout.best_clique_size))
            continue
        result_dct['true_clique_size'] = benchmarks[filepath]
        print(result_dct)
        results.append(result_dct)
        result_df = pd.DataFrame(results)
        result_df.to_csv(out_folder + f'results_{suffix}.csv')
        result_df.to_excel(out_folder + f'results_{suffix}.xlsx')
    return


if __name__ == '__main__':
    benchmarks = dict(**EASY,
                      **MEDIUM
                      )
    run_tests(benchmarks=benchmarks, time_limit=3600, suffix='EASY_MEDIUM')
