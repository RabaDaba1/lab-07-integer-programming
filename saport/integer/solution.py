from __future__ import annotations
from typing import List

import saport.simplex.expressions.expression as sseexp
import saport.simplex.solution as sssol
import saport.integer.model as simod


class Solution:
    """
        A class to represent a solution to linear integer programming problem.


        Attributes
        ----------
        model : Model
            model corresponding to the solution
        is_optimal: bool
            whether the solution is optimal
        is_feasible: bool
            whether the problem is feasible
        is_bounded: bool
            whether the problem is bounded
        assignment: List[float]
            list with the values assigned to the variables in the model if solution is feasible and bounded, otherwise None
            order of values should correspond to the order of variables in model.variables list

        Methods
        -------
        __init__(model: Model, assignment: list[int] | None, is_optimal: bool, is_feasible: bool, is_bounded: bool) -> Solution:
            constructs a new solution for the specified model and assignment  with the additional info if it is considered optimal
            if the assignment is null, one of the flags should false - either the solution is infeasible or is unbounded
        value(var: Variable) -> int | None:
            returns a value assigned to the specified variable if the model is feasible and bounded, otherwise None
        objective_value() -> float | None:
            returns a value of the objective function if the model is feasible and bounded, otherwise None
        has_assignment() -> bool:
            helper method returning info if the model is feasible and bounded, only then there is an assignment available
    
        Static Methods
        --------------
        with_linear_solution(model: simod.Model, solution: sssol.Solution) -> Solution:
            helper method to create solutions from simplex solutions
        with_assignment(model: simod.Model, assignment: List[int]) -> Solution:
            helper method to create solutions with valid assignments
        infeasible(model: simod.Model) -> Solution:    
            helper method to create infeasible solutions
        unbounded(model) -> Solution:
            helper method to create unbounded solutions
    """
    def __init__(self, model: simod.Model, assignment: List[int], is_optimal: bool, is_feasible: bool,
                 is_bounded: bool):
        self.model = model
        self.is_feasible = is_feasible
        self.is_bounded = is_bounded
        self.is_optimal = is_optimal
        self.assignment = assignment

    def value(self, var: sseexp.Variable) -> int:
        return None if self.assignment == None else self.assignment[var.index]

    def objective_value(self) -> float:
        return None if self.assignment == None else self.model.objective.evaluate(self.assignment)

    def has_assignment(self) -> bool:
        return self.assignment != None

    @staticmethod
    def with_assignment(model: simod.Model, assignment: List[float], is_optimal: bool):
        return Solution(model, assignment, is_optimal, True, True)

    @staticmethod
    def infeasible(model: simod.Model):
        return Solution(model, None, False, False, True)

    @staticmethod
    def unbounded(model):
        return Solution(model, None, False, True, False)

    @staticmethod
    def with_linear_solution(model: simod.Model, solution: sssol.Solution, is_optimal: bool) -> Solution:
        if solution is None:
            return None
        assignment = [round(v) for v in solution.assignment()] if solution.has_assignment() else None
        return Solution(model, assignment, is_optimal, solution.is_feasible, solution.is_bounded)

    def __str__(self):
        if not self.is_bounded:
            return "There is no solution, the model is unbounded"

        if not self.is_feasible:
            return "There is no solution, the model is infeasible"

        text = f'- objective value: {self.objective_value()}\n'
        text += '- solution is optimal\n' if self.is_optimal else ''
        text += '- assignment:'
        for var in self.model.variables:
            text += f'\n\t- {var.name} = {"{:.3f}".format(self.assignment[var.index])}'
        return text