# lp-lab1-branch-and-bound

Implementation of Branch-n-Bound algorithm for Max Clique Problem via cplex-solver

For tests execution run command:
```python
    python run_test.py
```

For certain benchmark execution run (e.g. *benchmarks/DIMACS_all_ascii/C125.9.clq*):
```python
python main.py --filepath benchmarks/DIMACS_all_ascii/C125.9.clq 
```

|    | benchmark          |   heuristic_clique_size |   bnb_clique_size | is_bnb_solution_clique   | bnb_exec_time   |   bnb_exec_time_seconds |   bnb_call_count |   bnb_max_recursion_depth |   true_clique_size |
|---:|:-------------------|------------------------:|------------------:|:-------------------------|:----------------|------------------------:|-----------------:|--------------------------:|-------------------:|
|  0 | johnson8-2-4.clq   |                       4 |                 4 | True                     | 0min 0.0sec     |               0.0188313 |                1 |                         0 |                  4 |
|  1 | johnson16-2-4.clq  |                       8 |                 8 | True                     | 0min 0.0sec     |               0.0169198 |                1 |                         0 |                  8 |
|  2 | MANN_a9.clq        |                      16 |                16 | True                     | 0min 0.3sec     |               0.328083  |               79 |                         8 |                 16 |
|  3 | keller4.clq        |                      11 |                11 | True                     | 0min 45.6sec    |              45.5648    |             3585 |                        46 |                 11 |
|  4 | c-fat200-1.clq     |                      12 |                12 | True                     | 0min 0.1sec     |               0.10893   |                1 |                         0 |                nan |
|  5 | c-fat500-1.clq     |                      14 |                14 | True                     | 0min 0.3sec     |               0.309799  |                1 |                         0 |                nan |
|  6 | c-fat500-10.clq    |                     126 |               126 | True                     | 0min 2.7sec     |               2.71867   |                1 |                         0 |                nan |
|  7 | c-fat200-2.clq     |                      24 |                24 | True                     | 0min 0.2sec     |               0.181097  |                1 |                         0 |                nan |
|  8 | hamming8-4.clq     |                      16 |                16 | True                     | 0min 1.2sec     |               1.23117   |                9 |                         4 |                 16 |
|  9 | gen200_p0.9_55.clq |                      38 |                55 | True                     | 0min 0.3sec     |               0.283433  |                3 |                         1 |                 55 |
| 10 | gen200_p0.9_44.clq |                      35 |                44 | True                     | 8min 27.0sec    |             506.989     |            61671 |                        40 |                 44 |
| 11 | C125.9.clq         |                      33 |                34 | True                     | 3min 58.4sec    |             238.351     |            33065 |                        35 |                 34 |
| 12 | p_hat300-1.clq     |                       8 |                 8 | True                     | 2min 22.3sec    |             142.292     |             6245 |                       165 |                  8 |
| 13 | brock200_2.clq     |                      10 |                12 | True                     | 3min 24.4sec    |             204.373     |            13941 |                       131 |                 12 |
| 14 | brock200_3.clq     |                      13 |                15 | True                     | 7min 2.6sec     |             422.551     |            22005 |                       122 |                 15 |
| 15 | brock200_4.clq     |                      14 |                17 | True                     | 32min 26.6sec   |            1946.56      |           144807 |                       119 |                 17 |
| 16 | brock200_1.clq     |                      20 |                21 | True                     | 82min 19.8sec   |            4939.82      |           246939 |                       100 |                 21 |
| 17 | p_hat1000-1.clq    |                       9 |                10 | True                     | TIMEOUT: >5400s |             nan         |              nan |                       nan |                 10 |
| 18 | san1000.clq        |                       8 |                11 | True                     | TIMEOUT: >5400s |             nan         |              nan |                       nan |                 15 |
