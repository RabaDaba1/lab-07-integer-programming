from abc import ABC, abstractmethod
from typing import List
from ..solver import Solver
from ..model import Problem, Solution, Item


class Heuristic(ABC):
    """
    A knapsack problem heuristic.

    Methods:
    --------
    __call__(item : Item) -> float:
        return a value representing how much the given items is valuable to the greedy algorithm
        bigger value > earlier to take in the backpack
    """

    @abstractmethod
    def __call__(self, item: Item) -> float:
        '''Override this method, it should use info in the item to calculate its priority'''
        

class GreedySolver(Solver):
    """
    A greedy solver for the knapsack problems.

    Attributes:
        heuristics: List[Heuristic]
            list of all the heuristics that should be tried
    """
    heuristics: List[Heuristic]

    def __init__(self, problem: Problem, timelimit: int, heuristics: List[Heuristic]):
        super().__init__(problem, timelimit)
        self.heuristics = heuristics

    def _solve_using_heuristic(self, heuristic: Heuristic) -> Solution:
        # TODO: implement the greedy solving strategy
        #      1) sort items in the problem by the `heuristic`
        #      2) take as many as you can
        #      3) remember to replace the dummy solution below :)
        # tip. don't implement sorting! Just use the "sorted" function
        return Solution([], 0, 0, False)


    def solve(self) -> Solution:
        self.start_timer()
        solutions = [self._solve_using_heuristic(h) for h in self.heuristics]
        self.stop_timer()
        return max(solutions, key=lambda s: s.value)


class DensityHeuristic(Heuristic):
    """
    Uses value/weight density of the item. 
    """
    def __call__(self, item: Item) -> float:
        # TODO: replace line below with the correct value
        return 0.0


class ValueHeuristic(Heuristic):
    """
    Uses value of the item. 
    """
    def __call__(self, item: Item) -> float:
        # TODO: replace line below with the correct value
        return 0.0


class WeightHeuristic(Heuristic):
    """
    Uses weight of the item. 
    """
    def __call__(self, item: Item) -> float:
        # TODO: replace line below with the correct value
        return 0.0