from __future__ import annotations
from .model import Problem
from enum import Enum
from collections import defaultdict
from .solver import Solver
from .solvers.bnb_dfs import BnbDFSSolver
from .solvers.dfs import DFSSolver
from .solvers.dynamic import DynamicSolver
from .solvers.greedy import GreedySolver, ValueHeuristic, WeightHeuristic, DensityHeuristic


class SolverType(Enum):
    """
    An enum representing all the available solver types.
    """
    GREEDY_VALUE = "greedy(value)"
    GREEDY_WEIGHT = "greedy(weight)"
    GREEDY_DENSITY = "greedy(density)"
    GREEDY_PORTFOLIO = "greedy(portfolio)"
    DYNAMIC = "dynamic"
    DFS = "dfs"
    BRANCH_AND_BOUND_DFS = "bnb(dfs)"


class SolverFactory:
    """
    A factory class creating solver objects.

    Static Methods:
    ---------------
    solver(type: SolverType, problem: Problem, timelimit: int) ->  Solver:
        creates a new solver object based on the specified type, given problem and timelimit
    """
    @staticmethod
    def solver(type: SolverType, problem: Problem, timelimit: int) -> Solver:
        return {
                SolverType.GREEDY_VALUE: GreedySolver(problem, timelimit, [ValueHeuristic()]),
                SolverType.GREEDY_WEIGHT: GreedySolver(problem, timelimit, [WeightHeuristic()]),
                SolverType.GREEDY_DENSITY: GreedySolver(problem, timelimit, [DensityHeuristic()]),
                SolverType.GREEDY_PORTFOLIO: GreedySolver(problem, timelimit, [DensityHeuristic(), ValueHeuristic(), WeightHeuristic()]),
                SolverType.DYNAMIC: DynamicSolver(problem, timelimit),
                SolverType.DFS: DFSSolver(problem, timelimit),
                SolverType.BRANCH_AND_BOUND_DFS: BnbDFSSolver(problem, timelimit),
            }[type]
