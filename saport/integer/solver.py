from abc import ABC, abstractmethod
from copy import deepcopy
from saport.simplex import solver as lpsolver
from saport.integer.model import Model
from saport.integer.solution import Solution
from saport.simplex.expressions import constraint as ssecon
from saport.simplex.expressions import expression as sseexp
from saport.simplex import solution as lpsolution
import math
import time 

class IntegerProgrammingSolver(ABC):
    """
        Abstract Integer Programming Solver

        Attributes
        ----------
        model : Model
            integer programming model to be solved
        timelimit: int
            what is the maximal solving time (in seconds)
        total_time: float
            how long it took to solve the problem
        start_time: float
            when the solving started
        interrupted: bool
            whether solving has been interrupted (by timeout)

        Methods
        -------
        start_timer():
            remember the starting time for the solver
        stop_timer():
            stores the total solving time
        wall_time() -> float:
            returns how long solver has been working
        timeout() -> bool:
            whether solver should stop working due to the timeout

        solve(model: Model, timelimit: int) -> Solution:
            solves the given model within a specified timelimit
        _solving
    """
    
    total_time = None
    start_time = None
    interrupted = False
    best_solution = None
    timelimit = 0

    def solve(self, model: Model, timelimit: int) -> Solution:
        self.timelimit = timelimit

        self.model = model

        self.start_timer()
        self._solving_routine()
        self.stop_timer()

        return self.best_solution
           
    def _lower_bound(self):
        return self.best_solution.objective_value() if self.best_solution != None and self.best_solution.has_assignment() else float('-inf') 

    @abstractmethod
    def _solving_routine(self):
        '''This method should be implemented in every integer programming solver'''

    def start_timer(self):
        self.start_time = time.time()

    def stop_timer(self):
        self.total_time = self.wall_time()

    def wall_time(self) -> float:
        return time.time() - self.start_time

    def timeout(self) -> bool:
        return self.wall_time() > self.timelimit
