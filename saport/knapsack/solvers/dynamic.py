from ..solver import Solver
from ..model import Solution, Item
import numpy as np
from typing import List



class DynamicSolver(Solver):
    """
    A naive dynamic programming solver for the knapsack problem.
    """

    def _create_table(self) -> np.ndarray:
        # TODO: fill the table!
        # tip 1. init table using np.zeros function (replace `None``)
        # tip 2. remember to handle timeout (refer to the dfs solver for an example)
        #        - just return the current state of the table
        table = None
        return table

    def _extract_solution(self, table: np.ndarray) -> Solution:
        used_items: List[Item] = []
        optimal = table[-1, -1] > 0

        # TODO: fill in the `used_items` list using info from the table!

        return Solution.from_items(used_items, optimal)

    def solve(self) -> Solution:
        self.interrupted = False
        self.start_timer()

        table = self._create_table()
        solution = self._extract_solution(table) if table is not None else Solution.empty()

        self.stop_timer()
        return solution
