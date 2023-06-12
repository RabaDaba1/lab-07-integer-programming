from copy import deepcopy
from saport.integer.solver import IntegerProgrammingSolver
from saport.simplex import solver as lpsolver
from saport.integer.model import Model
from saport.integer.solution import Solution
from saport.simplex.expressions import constraint as ssecon
from saport.simplex.expressions import expression as sseexp
from saport.simplex import solution as lpsolution
import math

class LinearRelaxationSolver(IntegerProgrammingSolver):
    """
        Naive branch and bound solver for general integer programming problems
        using a linear relaxation approach. 
    """  

    def _solving_routine(self):
        self._branch_and_bound(self.model)
        self.best_solution = Solution.with_linear_solution(self.model, self.best_solution, not self.interrupted)
           
    def _branch_and_bound(self, model: Model):
        # TODO: implement a branch and bound procedure analogically to the one in the knapsack solver
        #       1) use simplex[1] to find the upper bound[2]
        #       2) remember to handle infeasible and unbounded models[3]
        #       3) check the lower bound[4] and compare with the upper one
        #       4) look for a variable with float value[5]
        #          if there is none, update the `self.best_solution` if the solution is better than the old one
        #       5) check for timeout[6] and set the `self.interrupted` to `True` when it happens
        #       6) branch on the variable with the float value:
        #          - every branch has a different model exluding the current float value[7]
        #                     
        # [1] `lpsolver.Solver().solve(<model>)` 
        # [2] `solution.objective_value()`
        # [3] `solution.is_feasible`, `solution.is_bounded`, `solution.has_assignment()`
        # [4] `self._lower_bound()` inherited from the `Solver` class
        # [5] `self.find_float_assignment(<solution>)`
        # [6] `self.timeout()`
        # [7] `self._model_with_new_constraint(<model>, <constraint>)`
        
        raise NotImplementedError() 

        
    def _find_float_assignment(self, solution: lpsolution.Solution) -> sseexp.Variable:
        # TODO: find an variable[1] that has non-integer value[2] in the solution
        #      due to numeric errors some variables may have "almost integer" value, like 0.9999999 or 1.0000001
        #      make sure they are still counted as integers
        #      Make sure this method returns None if none of variables has a floating point value.
        #
        # [1] `self.model.variables` 
        # [2] `solution.value(<variable>)`
  
        return None

    def _model_with_new_constraint(self, model: Model, constraint: ssecon.Constraint) -> Model:
        new_model = deepcopy(model)
        new_model.add_constraint(constraint)
        return new_model
