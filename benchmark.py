from knapsack_benchmark import KnapsackBenchmark
from saport.knapsack.solverfactory import SolverType

problems = [
    "ks_4_0", "ks_19_0", "ks_lecture_dp_1", "ks_lecture_dp_2"
]

benchmark = KnapsackBenchmark(
    problems,
    solver_types=[
        # solvers to be benchmarked
        SolverType.GREEDY_VALUE,
        SolverType.GREEDY_WEIGHT,
        SolverType.GREEDY_DENSITY,
        SolverType.DYNAMIC,
        SolverType.BRANCH_AND_BOUND_DFS,
        SolverType.DFS,
        SolverType.INTEGER_IMPLICIT_ENUMERATION,
        SolverType.INTEGER_LINEAR_RELAXATION
    ],
)
benchmark.run()
