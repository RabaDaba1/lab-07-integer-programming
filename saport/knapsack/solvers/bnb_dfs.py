from ..model import Problem, Solution, Item
from typing import List
from ..solver import Solver


class BnbDFSSolver(Solver):
    """
    A branch-and-bound solver for the Knapsack Problem, 
    explores the search tree using a basic DFS strategy.
    
    Methods:
    --------
    _upper_bound(left : List[Item], solution: Solution) -> float:
        given the list of still available items and the current solution,
        calculates the linear relaxation of the problem
    """
    def dfs_bnb(self):
        self.best_solution = Solution.empty()
        return self._dfs_bnb(self.problem.items, self.best_solution)

    def _dfs_bnb(self, left: List[Item], solution: Solution):
        # TODO: implement a dfs branch-and-bound solver
        #
        #   tip 1. use the DFS code as your starting point (dfs.py)
        #   tip 2. use the _upper_bound method to calculate the upper bound
        #   tip 3. if the upper bound is lower than the current best solution, just
        #          ignore rest of the branch (a simple "return" is enough)
        return

    def _upper_bound(self, left: List[Item], solution: Solution) -> float:
        # TODO: implement the linear relaxation, i.e. assume you can take
        #      fraction of the items in the backpack
        #      return the value of such a solution
        #      tip 1. solution is your "starting point" (items already in the backpack)
        #      tip 2. left is the list of items you can still take
        #      tip 3. take the items with highest value density first (as in greedy_density approach)
        return 0.0

    def solve(self) -> Solution:
        self.interrupted = False
        self.start_timer()
        self.dfs_bnb()
        self.best_solution.optimal = not self.interrupted
        self.stop_timer()
        return self.best_solution