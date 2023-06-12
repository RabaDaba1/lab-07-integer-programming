import os
from pytest_mock import MockerFixture
import pytest
from saport.integer.solvers.implicit_enumeration import ImplicitEnumerationSolver
from saport.integer.solvers.linear_relaxation import LinearRelaxationSolver
from saport.integer.model import BooleanModel, Model
from saport.knapsack.solvers.integer_implicit_enumeration import IntegerImplicitEnumerationSolver
from saport.simplex.expressions.constraint import ConstraintType
from saport.simplex.expressions.expression import Expression
from saport.simplex.expressions.objective import ObjectiveType
import saport.simplex.model as lpmodel
import saport.simplex.solution as lpsol
from saport.knapsack.model import Problem
from saport.knapsack.solvers.integer_linear_relaxation import IntegerLinearRelaxationSolver

TEST_DIR = "knapsack_problems"
PROBLEM_NAMES = ["ks_lecture_dp_1", "ks_lecture_dp_2", "ks_4_0"]
TIMEOUT = 30

def indented_string(s: str, ident: str = '    '):
    return '\n'.join([ident + l for l in s.splitlines()])

@pytest.fixture()
def problems():
    return { problem_name : Problem.from_path(os.path.join(TEST_DIR, problem_name)) for problem_name in PROBLEM_NAMES }
    
def _create_test_model(obj_coeffs, cstr_coeffs, cstr_bounds, model_builder = Model):
    model = model_builder("test")
    vars = [model.create_variable(f"x_{i}") for i in range(len(obj_coeffs))]
    model.maximize(Expression.from_vectors(vars, obj_coeffs))
    for coeffs, b in zip(cstr_coeffs, cstr_bounds):
        model.add_constraint(Expression.from_vectors(vars, coeffs) <= b)
    return model

class TestLinearRelaxation:

    @pytest.mark.parametrize("problem_name, obj_coeffs, cstr_coeffs, cstr_bounds", [
        ("ks_lecture_dp_1", [5.0, 6.0, 3.0], [[4.0, 5.0, 2.0], [1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0]], [9, 1, 1, 1]),
        ("ks_lecture_dp_2", [16.0, 19.0, 23.0, 28.0], [[2.0, 3.0, 4.0, 5.0], [1.0, 0, 0, 0], [0, 1.0, 0, 0], [0, 0, 1.0, 0], [0, 0, 0, 1.0]], [7, 1, 1, 1, 1]),
        ("ks_4_0", [8.0, 10.0, 15.0, 4.0], [[4.0, 5.0, 8.0, 3.0], [1.0, 0, 0, 0], [0, 1.0, 0, 0], [0, 0, 1.0, 0], [0, 0, 0, 1.0]], [11, 1, 1, 1, 1])
    ])
    def test_knapsack_model_for_linear_relaxation_should_be_correct(self, problems, problem_name, obj_coeffs, cstr_coeffs, cstr_bounds):
        problem = problems[problem_name]
        solver = IntegerLinearRelaxationSolver(problem, TIMEOUT)
    
        model = solver._create_model()
        assert len(model.variables) == len(obj_coeffs), f"knapsack model for linear relaxation has incorrect number of variables (problem `{problem_name}`):" +\
            f"\n- got: {len(model.variables)}" +\
            f"\n- expected: {len(obj_coeffs)}" 
        assert model.objective is not None, f"knapsack model for linear relaxation is missing an objective (problem `{problem_name}`)"
        assert model.objective.type == ObjectiveType.MAX, f"knapsack model for linear relaxation has incorrect objective type {model.objective.type} (problem `{problem_name}`)"
        got_obj_coeffs = model.objective.expression.coefficients(model)
        assert got_obj_coeffs == obj_coeffs, f"knapsack model for linear relaxation has incorrect objective coefficients (problem `{problem_name}`):" +\
            f"\n- got: {got_obj_coeffs}" +\
            f"\n- expected: {obj_coeffs}"
        assert len(model.constraints) == len(cstr_bounds), f"knapsack model for linear relaxation has incorrect number of constraints (problem `{problem_name}`):" +\
            f"\n- got: {len(model.constraints)}" +\
            f"\n- expected: {len(cstr_bounds)}" 
        for coeffs, b in zip(cstr_coeffs, cstr_bounds):
            found = False
            for c in model.constraints:
                got_coeffs = c.expression.coefficients(model)
                if got_coeffs == coeffs and c.bound == b and c.type == ConstraintType.LE:
                    found = True
                    break
            assert found, f"knapsack model is missing constraint (problem `{problem_name}`)" +\
            f"\n- coeffs: {coeffs}" +\
            f"\n- bound: {len(obj_coeffs)}" +\
            f"\n- type: LE" +\
            f"\n- got model:\n{indented_string(str(model))}"


    @pytest.mark.parametrize("assignment, expected_var_index", [([1.0, 0.6, 1.0], 1),
        ([0.5, 1.0, 1.0], 0),
        ([1.0, 1.0, 0], None),
        ([1.0, 1.0, 0.5000000000000001, 0], 2),
        ([1.0, 0.33333333333333326, 1.0, 0], 1),
        ([0.0, 1.0, 1.0, 0], None),
        ([1.0, 0, 1.0, 0.19999999999999996], 3),
        ([1.0, 1.0, 0, 0.4000000000000001], 3),
        ([1.0, 0, 0, 1.0], None),
        ([1.0, 1.0, 0.25, 0], 2),
        ([0.0, 0.6, 1.0, 0], 1),
        ([0.75, 0, 1.0, 0], 0),
        ([0.0, 0, 1.0, 1.0], None),
        ([1.0, 1.0, 0, 0.6666666666666666], 3),
        ([0.75, 1.0, 0, 1.0], 0),
        ([1.0, 0.8, 0, 1.0], 1)])
    def test_solver_should_always_find_first_variable_with_non_integer_value_from_solution(self, assignment, expected_var_index):
        model = lpmodel.Model("test")
        for i in range(len(assignment)):
            model.create_variable(f"x_{i}")
        solver = LinearRelaxationSolver()
        solver.model = model 
        solution = lpsol.Solution(model, assignment, None, None, True, True)
        got = solver._find_float_assignment(solution)
        
        if expected_var_index is None:
            assert got is None, \
                f"found variable with float assignment, when there is none:" +\
                f"\n- got: {got}" +\
                f"\n- for assignment: {assignment}"
        else:
            assert got is not None and got.index == expected_var_index, \
                    f"failed to found the first variable with float value:" +\
                    f"\n- go index: {got.index if got is not None else None}" +\
                    f"\n- expected index: {expected_var_index}" +\
                    f"\n- for assignment: {assignment}"

    @pytest.mark.parametrize("obj_coeffs, cstr_coeffs, cstr_bounds, expected_assignment, bnb_calls", [
        ([5.0, 6.0, 3.0], [[4.0, 5.0, 2.0], [1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0]], [9, 1, 1, 1], [1, 1, 0], 5),
        ([16.0, 19.0, 23.0, 28.0], [[2.0, 3.0, 4.0, 5.0], [1.0, 0, 0, 0], [0, 1.0, 0, 0], [0, 0, 1.0, 0], [0, 0, 0, 1.0]], [7, 1, 1, 1, 1], [1, 0, 0, 1], 9),
        ([8.0, 10.0, 15.0, 4.0], [[4.0, 5.0, 8.0, 3.0], [1.0, 0, 0, 0], [0, 1.0, 0, 0], [0, 0, 1.0, 0], [0, 0, 0, 1.0]], [11, 1, 1, 1, 1], [0, 0, 1, 1], 13)])
    def test_linear_relaxation_should_perform_branch_and_bound_assuming_float_variable_is_selected_correctly(
            self, obj_coeffs, cstr_coeffs, cstr_bounds, expected_assignment, bnb_calls, mocker: MockerFixture):
  
        solver = LinearRelaxationSolver()
        model = _create_test_model(obj_coeffs, cstr_coeffs, cstr_bounds)
            
        bnb_spy = mocker.spy(obj=solver, name="_branch_and_bound")
        got_solution = solver.solve(model, TIMEOUT) 

        assert got_solution is not None and got_solution.assignment == expected_assignment, f"failed to correctly solve problem:" +\
                f"\n- got: {None if got_solution is None else got_solution.assignment}" +\
                f"\n- expected assignment: {expected_assignment}" +\
                f"\n- model: \n{indented_string(str(model))}"

        assert bnb_spy.call_count <= bnb_calls, f"branch and bound has not prune tree enough:" +\
            f"\n- `_branch_and_bound` has been run {bnb_spy.call_count} times" +\
            f"\n- correct implementation would be called just {bnb_calls} times" +\
            f"\n- model: \n{indented_string(str(model))}"

    


class TestImplicitEnumeration:

    @pytest.mark.parametrize("problem_name, obj_coeffs, cstr_coeffs, cstr_bounds", [
        ("ks_lecture_dp_1", [5.0, 6.0, 3.0], [[4.0, 5.0, 2.0]], [9]),
        ("ks_lecture_dp_2", [16.0, 19.0, 23.0, 28.0], [[2.0, 3.0, 4.0, 5.0]], [7]),
        ("ks_4_0", [8.0, 10.0, 15.0, 4.0], [[4.0, 5.0, 8.0, 3.0]], [11])
    ])
    def test_knapsack_model_for_implicit_enum_should_be_correct(self, problems, problem_name, obj_coeffs, cstr_coeffs, cstr_bounds):
        problem = problems[problem_name]
        solver = IntegerImplicitEnumerationSolver(problem, TIMEOUT)
    
        model = solver._create_model()
        assert len(model.variables) == len(obj_coeffs), f"knapsack model for implicit enumeration has incorrect number of variables (problem `{problem_name}`):" +\
            f"\n- got: {len(model.variables)}" +\
            f"\n- expected: {len(obj_coeffs)}" 
        assert model.objective is not None, f"knapsack model for implicit enumeration is missing an objective (problem `{problem_name}`)"
        assert model.objective.type == ObjectiveType.MAX, f"knapsack model for implicit enumeration has incorrect objective type {model.objective.type} (problem `{problem_name}`)"
        got_obj_coeffs = model.objective.expression.coefficients(model)
        assert got_obj_coeffs == obj_coeffs, f"knapsack model for implicit enumeration has incorrect objective coefficients (problem `{problem_name}`):" +\
            f"\n- got: {got_obj_coeffs}" +\
            f"\n- expected: {obj_coeffs}"
        assert len(model.constraints) == len(cstr_bounds), f"knapsack model for implicit enumeration has incorrect number of constraints (problem `{problem_name}`):" +\
            f"\n- got: {len(model.constraints)}" +\
            f"\n- expected: {len(obj_coeffs)}" 
        for coeffs, b in zip(cstr_coeffs, cstr_bounds):
            found = False
            for c in model.constraints:
                got_coeffs = c.expression.coefficients(model)
                if got_coeffs == coeffs and c.bound == b and c.type == ConstraintType.LE:
                    found = True
                    break
            assert found, f"knapsack model is missing constraint (problem `{problem_name}`)" +\
            f"\n- coeffs: {coeffs}" +\
            f"\n- bound: {len(obj_coeffs)}" +\
            f"\n- type: LE" +\
            f"\n- got model:\n{indented_string(str(model))}"

    
    @pytest.mark.parametrize("obj_coeffs, cstr_coeffs, cstr_bounds, expected_assignment, bnb_calls", [
        ([5.0, 6.0, 3.0], [[4.0, 5.0, 2.0]], [9], [1, 1, 0], 7),
        ([16.0, 19.0, 23.0, 28.0], [[2.0, 3.0, 4.0, 5.0]], [7], [1, 0, 0, 1], 13),
        ([8.0, 10.0, 15.0, 4.0], [[4.0, 5.0, 8.0, 3.0]], [11], [0, 0, 1, 1], 13)])
    def test_implicit_enumeration_should_perform_branch_and_bound_assuming_other_methods_are_implemented_correctly(
            self, obj_coeffs, cstr_coeffs, cstr_bounds, expected_assignment, bnb_calls, mocker: MockerFixture):
  
        solver = ImplicitEnumerationSolver()
        model = _create_test_model(obj_coeffs, cstr_coeffs, cstr_bounds, BooleanModel)
            
        bnb_spy = mocker.spy(obj=solver, name="_branch_and_bound")
        got_solution = solver.solve(model, TIMEOUT) 

        assert got_solution is not None and got_solution.assignment == expected_assignment, f"failed to correctly solve problem:" +\
                f"\n- got: {None if got_solution is None else got_solution.assignment}" +\
                f"\n- expected assignment: {expected_assignment}" +\
                f"\n- model: \n{indented_string(str(model))}"

        assert bnb_spy.call_count <= bnb_calls, f"branch and bound has not pruned tree enough:" +\
            f"\n- `_branch_and_bound` has been run {bnb_spy.call_count} times" +\
            f"\n- correct implementation would be called just {bnb_calls} times" +\
            f"\n- model: \n{indented_string(str(model))}"


    @pytest.mark.parametrize("obj_coeffs, constr_coeffs, constr_bounds, partial_assignment, expected_assignment", [
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {}, [0, 0, 0]),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {0: 1}, [1, 0, 0]),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {2: 1}, [0, 0, 1]),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {1: 1}, [0, 1, 0]),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {0: 1}, [1, 0, 0]),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {0: 0}, [0, 0, 0]),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {0: 0, 2: 1}, [0, 0, 1]),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {0: 0, 1: 1}, [0, 1, 0]),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {0: 0, 2: 1}, [0, 0, 1]),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {0: 0, 2: 0}, [0, 0, 0]),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {0: 0, 2: 0, 1: 1}, [0, 1, 0]),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {0: 0, 2: 0, 1: 1}, [0, 1, 0]),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {0: 0, 2: 0, 1: 0}, [0, 0, 0]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {}, [0, 0, 0, 0]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {0: 1}, [1, 0, 0, 0]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {1: 1}, [0, 1, 0, 0]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {2: 1}, [0, 0, 1, 0]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1}, [0, 0, 0, 1]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1}, [0, 0, 0, 1]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 0: 1}, [1, 0, 0, 1]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 1: 1}, [0, 1, 0, 1]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 2: 1}, [0, 0, 1, 1]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 0: 1}, [1, 0, 0, 1]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 0: 0}, [0, 0, 0, 1]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 0: 0, 1: 1}, [0, 1, 0, 1]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 0: 0, 2: 1}, [0, 0, 1, 1]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 0: 0, 1: 1}, [0, 1, 0, 1]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 0: 0, 1: 0}, [0, 0, 0, 1]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 0: 0, 1: 0, 2: 1}, [0, 0, 1, 1]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 0: 0, 1: 0, 2: 1}, [0, 0, 1, 1]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 0: 0, 1: 0, 2: 0}, [0, 0, 0, 1]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0}, [0, 0, 0, 0]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0, 0: 1}, [1, 0, 0, 0]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0, 1: 1}, [0, 1, 0, 0]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0, 2: 1}, [0, 0, 1, 0]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0, 2: 1}, [0, 0, 1, 0]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0, 2: 1, 0: 1}, [1, 0, 1, 0]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0, 2: 1, 1: 1}, [0, 1, 1, 0]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0, 2: 1, 1: 1}, [0, 1, 1, 0]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0, 2: 1, 1: 0}, [0, 0, 1, 0]),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0, 2: 0}, [0, 0, 0, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {}, [0, 0, 0, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {0: 1}, [1, 0, 0, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1}, [0, 0, 1, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {3: 1}, [0, 0, 0, 1]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {1: 1}, [0, 1, 0, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1}, [0, 0, 1, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 1}, [1, 0, 1, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 3: 1}, [0, 0, 1, 1]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 1: 1}, [0, 1, 1, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 1}, [1, 0, 1, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 0}, [0, 0, 1, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 0, 3: 1}, [0, 0, 1, 1]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 0, 1: 1}, [0, 1, 1, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 0, 3: 1}, [0, 0, 1, 1]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 0, 3: 0}, [0, 0, 1, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 0, 3: 0, 1: 1}, [0, 1, 1, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 0, 3: 0, 1: 1}, [0, 1, 1, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 0, 3: 0, 1: 0}, [0, 0, 1, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0}, [0, 0, 0, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0, 0: 1}, [1, 0, 0, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0, 3: 1}, [0, 0, 0, 1]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0, 1: 1}, [0, 1, 0, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0, 1: 1}, [0, 1, 0, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0, 1: 1, 0: 1}, [1, 1, 0, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0, 1: 1, 3: 1}, [0, 1, 0, 1]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0, 1: 1, 0: 1}, [1, 1, 0, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0, 1: 1, 0: 0}, [0, 1, 0, 0]),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0, 1: 0}, [0, 0, 0, 0])
    ])
    def test_solver_should_find_the_best_possible_assignment(self, 
        obj_coeffs, constr_coeffs, constr_bounds, partial_assignment, expected_assignment):
        model = _create_test_model(obj_coeffs, constr_coeffs, constr_bounds)
        solver = ImplicitEnumerationSolver()
        solver._enum_model = model
        partial_assignment = {model.variables[i] : v for i,v in partial_assignment.items()} 
        got_assignment = solver._best_possible_assignment(partial_assignment)
        assert got_assignment == expected_assignment, \
            f"the best possible assignment is not correct:" +\
            f"\n- got: {got_assignment}" +\
            f"\n- expected: {expected_assignment}" +\
            f"\n- enum model:\n{indented_string(str(model))}" +\
            f"\n- for partial assignment: {partial_assignment}"
    
    @pytest.mark.parametrize("obj_coeffs, constr_coeffs, constr_bounds, partial_assignment, expected_bool", [
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {}, True),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {2: 1}, True),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {2: 0}, True),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {2: 0, 0: 0}, True),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {2: 0, 0: 0, 1: 0}, False),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {}, True),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1}, True),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 2: 1}, True),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 2: 0}, True),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 2: 0, 1: 1}, True),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 2: 0, 1: 0}, True),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 2: 0, 1: 0, 0: 1}, True),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 1, 2: 0, 1: 0, 0: 0}, False),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0}, True),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0, 2: 1}, True),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0, 2: 1, 1: 1}, True),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0, 2: 1, 1: 0}, False),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {3: 0, 2: 0}, False),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {}, True),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1}, True),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 1}, True),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 0}, True),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 0, 3: 1}, True),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 0, 3: 0}, True),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 1, 0: 0, 3: 0, 1: 0}, False),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0}, True),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0, 1: 1}, True),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0, 1: 1, 0: 1}, True),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0, 1: 1, 0: 0}, False),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {2: 0, 1: 0}, False)
         ])
    def test_solver_should_determine_if_partial_assignment_is_satisfiable(self, 
        obj_coeffs, constr_coeffs, constr_bounds, partial_assignment, expected_bool):
        model = _create_test_model(obj_coeffs, constr_coeffs, constr_bounds)
        solver = ImplicitEnumerationSolver()
        solver._enum_model = model
        partial_assignment = {model.variables[i] : v for i,v in partial_assignment.items()} 
        got_bool = solver._is_model_satisfiable_with_partial_assignment(partial_assignment)
        assert got_bool == expected_bool, \
            f"failed to assess if the partial assignment is satisfiable:" +\
            f"\n- got: {got_bool}" +\
            f"\n- expected: {expected_bool}" +\
            f"\n- enum model:\n{indented_string(str(model))}" +\
            f"\n- for partial assignment: {partial_assignment}"

    @pytest.mark.parametrize("obj_coeffs, constr_coeffs, constr_bounds, left, partial_assignment, expected_index", [
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {0, 1, 2}, {}, 0),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {1, 2}, {0: 0}, 1),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], {2}, {0: 0, 1: 0}, 2),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {0, 1, 2, 3}, {}, 3),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {0, 1, 2}, {3: 1}, 0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {1, 2}, {3: 1, 0: 0}, 1),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {2}, {3: 1, 0: 0, 1: 0}, 2),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {0, 1, 2}, {3: 0}, 2),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], {0, 1}, {3: 0, 2: 1}, 1),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {0, 1, 2, 3}, {}, 2),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {0, 1, 3}, {2: 1}, 0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {1, 3}, {2: 1, 0: 0}, 1),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {3}, {2: 1, 0: 0, 1: 0}, 3),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {0, 1, 3}, {2: 0}, 1),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], {0, 3}, {2: 0, 1: 1}, 0)
         ])
    def test_solver_should_find_variable_with_least_infeasibility(self, 
        obj_coeffs, constr_coeffs, constr_bounds, left, partial_assignment, expected_index):
        model = _create_test_model(obj_coeffs, constr_coeffs, constr_bounds)
        solver = ImplicitEnumerationSolver()
        solver._enum_model = model
        partial_assignment = {model.variables[i] : v for i,v in partial_assignment.items()}
        left = {model.variables[i] for i in left}
        expected_var = model.variables[expected_index]

        got_var = solver._select_var_to_branch(left, partial_assignment)
        assert got_var == expected_var, \
            f"variable to branch is not correct:" +\
            f"\n- got: {got_var}" +\
            f"\n- expected: {expected_var}" +\
            f"\n- enum model:\n{indented_string(str(model))}" +\
            f"\n- left: {left}" +\
            f"\n- for partial assignment: {partial_assignment}"

    @pytest.mark.parametrize("obj_coeffs, constr_coeffs, constr_bounds, assignment, expected", [
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], [0, 0, 0], 2.0),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], [1, 0, 0], 0),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], [0, 1, 0], 0),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], [0, 0, 1], 0),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], [1, 0, 0], 0),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], [0, 0, 0], 2.0),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], [0, 0, 1], 0),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], [0, 1, 0], 0),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], [0, 0, 0], 2.0),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], [0, 0, 1], 0),
         ([-5.0, -6.0, -3.0], [[-4.0, -5.0, -2.0]], [-2.0], [0, 0, 1], 0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 0, 0, 0], 7.0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 1, 0, 0], 4.0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 0, 0, 1], 2.0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [1, 0, 0, 0], 5.0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 0, 1, 0], 3.0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 0, 0, 1], 2.0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 1, 0, 1], 0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [1, 0, 0, 1], 0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 0, 1, 1], 0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [1, 0, 0, 1], 0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 0, 0, 1], 2.0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 1, 0, 1], 0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 0, 1, 1], 0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 0, 0, 1], 2.0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 0, 1, 1], 0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 0, 0, 0], 7.0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 1, 0, 0], 4.0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [1, 0, 0, 0], 5.0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 0, 1, 0], 3.0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 0, 1, 0], 3.0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 1, 1, 0], 0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [1, 0, 1, 0], 1.0),
         ([-16.0, -19.0, -23.0, -28.0], [[-2.0, -3.0, -4.0, -5.0]], [-7.0], [0, 1, 1, 0], 0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 0, 0, 0], 9.0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 0, 0, 1], 6.0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 1, 0, 0], 4.0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 0, 1, 0], 1.0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [1, 0, 0, 0], 5.0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 0, 1, 0], 1.0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 0, 1, 1], 0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 1, 1, 0], 0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [1, 0, 1, 0], 0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [1, 0, 1, 0], 0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 0, 1, 0], 1.0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 0, 1, 1], 0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 1, 1, 0], 0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 0, 1, 0], 1.0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 0, 1, 1], 0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 0, 1, 1], 0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 0, 0, 0], 9.0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 0, 0, 1], 6.0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 1, 0, 0], 4.0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [1, 0, 0, 0], 5.0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 1, 0, 0], 4.0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [0, 1, 0, 1], 1.0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [1, 1, 0, 0], 0),
         ([-8.0, -10.0, -15.0, -4.0], [[-4.0, -5.0, -8.0, -3.0]], [-9.0], [1, 1, 0, 0], 0)
    ])
    def test_solver_should_assess_total_infeasibility_of_assignment(self,
        obj_coeffs, constr_coeffs, constr_bounds, assignment, expected):
        model = _create_test_model(obj_coeffs, constr_coeffs, constr_bounds)
        solver = ImplicitEnumerationSolver()
        solver._enum_model = model
        got = solver._total_infeasibility(assignment)
        assert got == expected, \
            f"total infeasibilty is incorrect:" +\
            f"\n- got: {got}" +\
            f"\n- expected: {expected}" +\
            f"\n- enum model:\n{indented_string(str(model))}" +\
            f"\n- for assignment: {assignment}"