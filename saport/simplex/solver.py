from __future__ import annotations
import sys
from typing import Dict, List

from copy import deepcopy
import saport.simplex.model as ssmod
import saport.simplex.expressions.objective as sseobj
import saport.simplex.expressions.constraint as ssecon
import saport.simplex.expressions.expression as sseexp
import saport.simplex.solution as sssol
import saport.simplex.tableau as sstab
import numpy as np

class Solver:
    """
        A class to represent a simplex solver.

        Attributes:
        ______
        _slacks: Dict[Variable, Constraint]:
            contains mapping from slack variables to their corresponding constraints
        _surpluses: Dict[Variable, Constraint]:
            contains mapping from surplus variables to their corresponding constraints
        _artificial: Dict[Variable, Constraint]:
            contains mapping from artificial variables to their corresponding constraints

        Methods
        -------
        solve(model: Model) -> Tableau:
            solves the given model and return the first solution
    """
    _slacks: Dict[sseexp.Variable, ssecon.Constraint]
    _surpluses: Dict[sseexp.Variable, ssecon.Constraint]
    _artificial: Dict[sseexp.Variable, ssecon.Constraint]

    def solve(self, model: ssmod.Model):
        normal_model = self._augment_model(model)
        if len(self._slacks) < len(normal_model.constraints):
            tableau, success = self._presolve(normal_model)
            if not success:
                return sssol.Solution.infeasible(model, tableau, tableau)
        else:
            tableau = self._basic_initial_tableau(normal_model)

        initial_tableau = deepcopy(tableau)
        if self._optimize(tableau) == False:
            return sssol.Solution.unbounded(model, initial_tableau, tableau)

        assignment = tableau.extract_assignment()
        return self._create_solution(assignment, model, initial_tableau, tableau)

    def _optimize(self, tableau: sstab.Tableau):
        while not tableau.is_optimal():
            pivot_col = tableau.choose_entering_variable()
            if tableau.is_unbounded(pivot_col):
                return False
            pivot_row = tableau.choose_leaving_variable(pivot_col)

            tableau.pivot(pivot_row, pivot_col)
        return True

    def _presolve(self, model: ssmod.Model):
        """
            _presolve(model: Model) -> Tableau:
                returns a initial tableau for the second phase of simplex
        """
        presolve_model = self._create_presolve_model(model)
        tableau = self._presolve_initial_tableau(presolve_model)

        self._optimize(tableau)

        if self._artifical_variables_are_positive(tableau):
            return (tableau, False)

        tableau = self._restore_initial_tableau(tableau, model)
        return (tableau, True)

    def _augment_model(self, original_model: ssmod.Model):
        """
            _augment_model(model: Model) -> Model:
                returns an augmented version of the given model
        """
        model = deepcopy(original_model)
        model.simplify()
        self._change_objective_to_max(model)
        self._change_constraints_bounds_to_nonnegative(model)
        self._slacks = self._add_slack_variables(model)
        self._surpluses = self._add_surplus_variables(model)
        return model

    def _create_presolve_model(self, augmented_model: ssmod.Model):
        presolve_model = deepcopy(augmented_model)
        self._artificial = self._add_artificial_variables(presolve_model)
        return presolve_model

    def _change_objective_to_max(self, model: ssmod.Model):
        if model.objective.type == sseobj.ObjectiveType.MIN:
            model.objective.invert()


    def _change_constraints_bounds_to_nonnegative(self, model: ssmod.Model):
        for constraint in model.constraints:
            if constraint.bound < 0:
                constraint.invert()

    def _add_slack_variables(self, model: ssmod.Model) -> List[sseexp.Variable]:
        slacks: Dict[sseexp.Variable, ssecon.Constraint] = dict()

        for constraint in model.constraints:
            if constraint.type == ssecon.ConstraintType.LE:
                slack_var = model.create_variable(f"s{constraint.index}")
                slacks[slack_var] = constraint
                constraint.expression += slack_var
                constraint.type = ssecon.ConstraintType.EQ
        return slacks

    def _add_surplus_variables(self, model: ssmod.Model) -> List[sseexp.Variable]:
        surpluses: Dict[sseexp.Variable, ssecon.Constraint] = dict()
        for constraint in model.constraints:
            if constraint.type == ssecon.ConstraintType.GE:
                surplus_var = model.create_variable(f"s{constraint.index}")
                surpluses[surplus_var] = constraint
                constraint.expression -= surplus_var
                constraint.type = ssecon.ConstraintType.EQ
        return surpluses

    def _add_artificial_variables(self, model: ssmod.Model):
        artificial_variables: Dict[sseexp.Variable, ssecon.Constraint] = dict()
        for constraint in model.constraints.copy():
            if len([c for c in self._slacks.values() if c.index == constraint.index]) > 0:
                continue
            artificial_var = model.create_variable(f"R{constraint.index}")
            artificial_variables[artificial_var] = constraint
            constraint.expression += artificial_var
        return artificial_variables

    def _presolve_initial_tableau(self, model: ssmod.Model):
        objective_row = np.array([0.0 for _ in model.variables] + [0.0])

        for var in self._artificial.keys():
            objective_row[var.index] = 1.0

        table = np.array([objective_row] + [c.expression.coefficients(model) + [c.bound] for c in model.constraints])

        for c in self._artificial.values():
            constraint = model.constraints[c.index]
            factors_row = np.array(constraint.expression.coefficients(model) + [constraint.bound])
            objective_row -= factors_row

        table = np.array([objective_row] + [c.expression.coefficients(model) + [c.bound] for c in model.constraints])
        return sstab.Tableau(model, table)

    def _basic_initial_tableau(self, model: ssmod.Model):
        objective_row = np.array((-1 * model.objective.expression).coefficients(model) + [0.0])
        table = np.array([objective_row] + [c.expression.coefficients(model) + [c.bound] for c in model.constraints])
        return sstab.Tableau(model, table)

    def _artifical_variables_are_positive(self, tableau: sstab.Tableau): 
        assignment = tableau.extract_assignment()
        for variable in self._artificial:
            if assignment[variable.index] > sstab.eps:
                return True
        return False


    def _restore_initial_tableau(self, tableau, model):
        basis = tableau.extract_basis()
        tableau = self._remove_artificial_variables(tableau)
        tableau = self._restore_original_objective_row(tableau, model)
        tableau = self._fix_objective_row_to_the_basis(tableau, basis)
        return tableau

    def _remove_artificial_variables(self, tableau: sstab.Tableau):
        columns_to_remove = [var.index for var in self._artificial.keys()]
        table = np.delete(tableau.table, columns_to_remove, 1)
        return sstab.Tableau(tableau.model, table)

    def _restore_original_objective_row(self, tableau: sstab.Tableau, model: ssmod.Model):
        objective_row = np.array((-1 * model.objective.expression).coefficients(model) + [0.0])
        new_table = np.array(tableau.table)
        new_table[0] = objective_row
        return sstab.Tableau(model, new_table)

    def _fix_objective_row_to_the_basis(self, tableau: sstab.Tableau, basis: List[int]):
        objective_row = tableau.table[0].copy()

        for (constr_index, col) in enumerate(basis):
            if col >= len(objective_row) - 1:
                continue

            row = constr_index + 1
            objective_factor = objective_row[col]
            if objective_factor == 0:
                continue
            objective_row -= objective_factor * tableau.table[row]

        new_table = np.array(tableau.table)
        new_table[0] = objective_row
        return sstab.Tableau(tableau.model, new_table)

    def _create_solution(self, assignment: List[float], model: ssmod.Model, initial_tableau: sstab.Tableau, tableau: sstab.Tableau):
        return sssol.Solution.with_assignment(model, assignment, initial_tableau, tableau)