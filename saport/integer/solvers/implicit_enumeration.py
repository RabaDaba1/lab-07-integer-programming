from copy import deepcopy
from typing import Set, Dict, List

from saport.integer.solver import IntegerProgrammingSolver
from saport.integer.model import BooleanModel
from saport.integer.solution import Solution
from saport.simplex.expressions import expression as sseexp
from saport.simplex.expressions import constraint as ssecon
from saport.simplex.expressions import expression as sseexp
from saport.simplex.expressions import objective as sseobj

class UnsupportedModel(Exception):
    pass


class ImplicitEnumerationSolver(IntegerProgrammingSolver):
    """
        Naive branch and bound solver for boolean integer programming problems
        using an implicit enumeration approach.

        Attributes:
        ----------
        _flipped_variables: Set[Variable]
            variables that had to be "flipped" in order to get an enumerable model
    """
    _flipped_variables: Set[sseexp.Variable]

    def __init__(self):
        self._flipped_variables = set()

    def _solving_routine(self):
        if not isinstance(self.model, BooleanModel):
            raise UnsupportedModel(
                f"the model of type {type(self.model)} is not supported by the implicit enumeration solver")
        self.model.simplify()
        self._enum_model = self._preprocess_model(deepcopy(self.model))
        self._branch_and_bound(dict(), set(self._enum_model.variables))

        if self.best_solution is None:
            self.best_solution = Solution.infeasible(self.model)
        else:
            self.best_solution = self._unflipped_solution(self.best_solution)

    def _preprocess_model(self, model: BooleanModel) -> BooleanModel:
        _enumerable_model = deepcopy(model)
        _enumerable_model.simplify()

        def change_objective_to_max(model: BooleanModel):
            if model.objective.type == sseobj.ObjectiveType.MIN:
                model.objective.invert()

        def change_constraints_bounds_to_LE(model: BooleanModel):
            for constraint in model.constraints.copy():
                if constraint.type == ssecon.ConstraintType.EQ:
                    constraint.type = ssecon.ConstraintType.LE
                    model.add_constraint(constraint.expression >= constraint.bound)
            for constraint in model.constraints:
                if constraint.type == ssecon.ConstraintType.GE:
                    constraint.invert()

        def flip_variables(model: BooleanModel):
            def variables_to_flip(model: BooleanModel) -> Set[sseexp.Variable]:
                objective_coeffs = model.objective.expression.coefficients(model)
                return {model.variables[i] for i, c in enumerate(objective_coeffs) if c > 0}

            def flip_variable(var: sseexp.Variable, model: BooleanModel):
                coeff = model.objective.expression.get_coefficient(var)
                model.objective.expression.set_coefficient(var, -coeff)

                for c in model.constraints:
                    coeff = c.expression.get_coefficient(var)
                    if coeff == 0.0:
                        continue
                    c.expression.set_coefficient(var, -coeff)
                    c.bound = c.bound - coeff

            self._flipped_variables = variables_to_flip(model)
            for v in self._flipped_variables:
                flip_variable(v, model)

        change_objective_to_max(_enumerable_model)
        change_constraints_bounds_to_LE(_enumerable_model)
        flip_variables(_enumerable_model)

        return _enumerable_model
    
    def _unflipped_solution(self, solution: Solution) -> Solution:
        assignment = [(1 - solution.value(var)) if var in self._flipped_variables else solution.value(var)
                      for var in self._enum_model.variables]
        return Solution.with_assignment(self.model, assignment, is_optimal=not self.interrupted)

    def _branch_and_bound(self, partial_assignment: Dict[sseexp.Variable, int], left: Set[sseexp.Variable]) -> None:
        """
            Performs a branch and bound search using implicit enumeration strategy.
            This recursive method returns `None` and should just update the self.best_solution. 

            Arguments:
            ----------
            partial_assignment: Dict[Variable, int]
                variables with already assigned (integer) values
            left: Set[Variable]
                variables still left to be assigned
        """
        # TODO: 1) find the best possible assignment containing the partial assignment[1]
        #          then the upper bound is the objective value[2] of this assignment
        #       2) if the upper bound is lower than the current lower bound[2], then the branch may be pruned
        #          as in every other branch and bound algorithm 
        #       3) then check if the partial assignment is still satisfiable[3]
        #          if it's not, then the branch should be pruned
        #       4) then check if it's feasible solution[4]
        #          if yes, then prune the branch and update the self.best_solution as necessary[5]
        #       5) check for timeout[6] and if it's the case, set self.interrupted to True and finish
        #       6) otherwise, choose the branching variable[7] and branch on it
        #          remember to branch with updated "left" and "partial_assignment"
        #
        # [1] `self._best_possible_assignment(<partial assignment>)`
        # [2] `self._enum_model.objective.evaluate(<assignment>)``
        # [3] `self._lower_bound()` which is inherited from the `Solver` class
        # [4] `self._is_model_satisfiable_with_partial_assignment(<partial assignment>)`
        # [5] `self._total_infeasibilty(<best possible assignment>)` as to be equal zero
        # [6] `Solution.with_assignment(self._enum_model, <best possible assignment>, False)`
        # [7] `self.timeout()`
        # [8] `self._select_var_to_branch(left, partial_assignment)`

        raise NotImplementedError()

    def _best_possible_assignment(self, partial_assignment: Dict[sseexp.Variable, int]) -> List[int]:
        # TODO: This methods create an assignment (list of integers corresponding to the variables[1])    
        #       satisfying following conditions:
        #       - if the variable has a value in `partial_assignment` it should be the same in the output assignment
        #       - otherwise the value should be `0`
        #
        # [1] self._enum_model.variables

        return []

    def _is_model_satisfiable_with_partial_assignment(self, partial_assignment: Dict[sseexp.Variable, int]) -> bool:
        # TODO: Check for each constraint whether the partial assignments can be extended to satisfy the constraint
        #       1) create an "optimistic" assignment based on the partial_assignment and the tested constraint
        #          - variables fixed in the assignment should have value as fixed
        #          - other ones should be 1 if they have negative coefficient in the constraint[1], otherwise 0
        #       2) evaluate the constraint expression[2] and check if it satisfies the bound[3]
        #       3) if at least one constraint can't be satisfied, the model is not satisfiable
        #
        # [1] constraint.expression.coefficients(self._enum_model)
        # [2] constraint.expression.evaluate(<assignment>)
        # [3] constraint.bound (remember that enum model contains only LE constraints)

        return True

    def _select_var_to_branch(self, left: Set[sseexp.Variable], partial_assignment: Dict[sseexp.Variable,
                                                                                         int]) -> sseexp.Variable:
        # TODO: for every variable in the problem, check what would be the total infeasibility[1], 
        #       if the variable was assigned 1 and all the remaining variables were set to 0[2]
        # 
        #       Return variable with the least infeasibility (replace left.pop()).
        #       I case of a tie choose variable with the smallest index.
        #
        # [1] self._total_infeasibility(<assignment>)
        # [2] self._best_possible_assignment(<partial assignment>)

        return left.pop()

    def _total_infeasibility(self, assignment: List[int]) -> int:
        total_infeasibility = 0
        # TODO: check how much the constraints are violated.
        #       For each constraint evaluate the constraint expression[1] 
        #       and check how much its value surraise NotImplementedError()es the bound.
        #       Then add the result to the total_infeasibility
        #
        # [1] constraint.expression.evaluate(<assignment>)

        return total_infeasibility

    
