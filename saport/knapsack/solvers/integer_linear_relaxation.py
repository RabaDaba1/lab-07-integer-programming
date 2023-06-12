from saport.knapsack.solver import Solver
from saport.knapsack.model import Problem, Solution, Item
from typing import List
from saport.integer.model import Model
from saport.integer.solvers.linear_relaxation import LinearRelaxationSolver
from saport.simplex.expressions.expression import Expression


class IntegerLinearRelaxationSolver(Solver):
    """
    An Integer Programming solver for the knapsack problems

    Methods:
    --------
    _create_model() -> Model:
        creates and returns an integer programming model based on the self.problem
    """
    def _create_model(self) -> Model:
        m = Model('knapsack')
        # TODO:
        # - variables: whether the item gets taken
        # - constraints: weights
        # - objective: values
        return m

    def solve(self) -> Solution:
        m = self._create_model()
        solver = LinearRelaxationSolver()
        integer_solution = solver.solve(m, self.timelimit)
        items = [item for (i, item) in enumerate(self.problem.items) if integer_solution.value(m.variables[i]) > 0]
        solution = Solution.from_items(items, not solver.interrupted)
        return solution