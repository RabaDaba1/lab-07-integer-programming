from copy import deepcopy
from saport.simplex import model as lpmodel
from saport.simplex import solution as sssol

class DeprecatedMethod(BaseException):
    pass

class Model(lpmodel.Model):
    """
        An integer programming model.
        It has the same the same structure as the linear programming model, but the variables are implicitly treated as integers.
        
        Attributes:
        ----------
        solver: Solver
        solver used to solve the model. Useful when one wants to check some statistics, solving time, etc. 
    """

    def __str__(self):
        separator = '\n\t'
        text = f'''- name: {self.name}
- variables:{separator}{separator.join([f"{v.name} ∈ ℕ" for v in self.variables])}
- constraints:{separator}{separator.join([str(c) for c in self.constraints])}
- objective:{separator}{self.objective}
'''
        return text

    def solve(self) -> sssol.Solution:
        raise DeprecatedMethod("don't use this method, rather try to create a separate solver object")


class BooleanModel(Model):
    """
        A boolean integer programming model.
        It has exactly the same structure, but the variables are implicitly treated as booleans (domains {0,1})
    """

    def __str__(self):
        separator = '\n\t'
        text = f'''- name: {self.name}
- variables:{separator}{separator.join([f"{v.name} ∈ {{0,1}}" for v in self.variables])}
- constraints:{separator}{separator.join([str(c) for c in self.constraints])}
- objective:{separator}{self.objective}
'''
        return text

    def solve(self) -> sssol.Solution:
        raise DeprecatedMethod("don't use this method, rather try to create a separate solver object")