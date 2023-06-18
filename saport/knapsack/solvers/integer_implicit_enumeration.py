from saport.knapsack.solver import Solver
from saport.knapsack.model import Problem, Solution, Item
from typing import List
from saport.integer.model import BooleanModel
from saport.integer.solvers.implicit_enumeration import ImplicitEnumerationSolver
from saport.simplex.expressions.expression import Expression


class IntegerImplicitEnumerationSolver(Solver):
    """
    An Integer Programming solver for the knapsack problems

    Methods:
    --------
    _create_model() -> Model:
        creates and returns an integer programming model based on the self.problem
    """
    def _create_model(self) -> BooleanModel:
        m = BooleanModel('knapsack')
        # TODO:
        # - variables: whether the item gets taken
        # - constraints: weights
        # - objective: values
        
        objective = Expression()
        weights = Expression()
        
        for item in self.problem.items:
            variable = m.create_variable(f"x_{item.index}")
            
            objective += item.value * variable
            weights += item.weight * variable
            
        m.add_constraint(weights <= self.problem.capacity)
        m.maximize(objective)
        
        return m

    def solve(self) -> Solution:
        m = self._create_model()
        solver = ImplicitEnumerationSolver()
        integer_solution = solver.solve(m, self.timelimit)
        items = [item for (i, item) in enumerate(self.problem.items) if integer_solution.value(m.variables[i]) > 0]
        solution = Solution.from_items(items, not solver.interrupted)
        return solution