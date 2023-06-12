# Lab 07 - Integer Programming

The goal of this is lab is to implement to Integer Programming algorithms and apply them to the knapsack problem:

* fill missing code in: 
  * `saport.knapsack.solvers.integer_implicit_enumeration`
  * `saport.knapsack.solvers.integer_linear_relaxation`
  * `saport.integer.solvers.implicit_relaxation`
  * `saport.integer.solvers.linear_relaxation`

* you may use the `benchmark.py` to compare your generic implementations with the knapsack specific ones

## SAPORT

SAPORT = Student's Attempt to Produce an Operation Research Toolkit

The project depends on the fairly recent numpy distribution and Python interpreter (version >= `3.9` is recommended). All depedendencies are listed in `requirements.txt`. One can install them with simple `pip install -r requirements.txt`, but using a virtual environment (e.g. virtualenv) is encouraged ([official tutorial](https://docs.python.org/3/tutorial/venv.html)). 

## Unit Tests

The `tests` folder contains unit tests written using `pytest`. 
Run it via `pytest`/`pycharm`/`vscode`.

## Benchmark

The `knapsack_problems` folder contains some input instances. You may benchmark your solvers by running: `python benchmark.py`.
This script is **not** used in the grading process. You may want to edit the `benchmark.py` to enable/disable solvers or problems.

## GitLab Setup 

* [ ] Make sure, you have a **private** group 
  * [how to create a group](https://docs.gitlab.com/ee/user/group/#create-a-group)
* [ ] Add @bobot-is-a-bot as the new group member (role: **maintainer**)
  * [how to add a group member](https://docs.gitlab.com/ee/user/group/#add-users-to-a-group)
* [ ] Fork this project into your new **private** group
  * [how to create a fork](https://docs.gitlab.com/ee/user/project/repository/forking_workflow.html#creating-a-fork)

## How To Submit Solutions

* [ ] Clone repository: git clone:
    ```bash 
    git clone <repository url>
    ```
* [ ] Solve the exercises 
    * remember to change only files with `#TODO` comments
* [ ] Commit your changes
    ```bash
    git add <path to the changed files>
    git commit -m <commit message>
    ```
* [ ] Push changes to the gitlab master branch
    ```bash
    git push -u origin master
    ```

The rest will be taken care of automatically. You can check the `GRADE.md` file for your grade / test results. Be aware that it may take some time (up to one hour) till this file appears / gets updated. 

## Repository Guide

```bash
.
├── README.md     # this README
├── conftest.py   # this file makes sure pytest works correctly 
├── benchmark.py  # script to run a solver benchmark
├── knapsack_benchmark.py # benchmark implementation
├── requirements.txt      # python libraries required by the problem
├── knapsack_problems     # this folder contains some example inputs used in tests
├── saport 
│   ├── integer   # folder with integer programming solver
│   │    ├── model.py     # model classes for the integer programming problems
│   │    ├── solution.py  # solution class, representing the integer programming solution
│   │    ├── solver.py    # abstract class, that has to be implemented by every interger programming solver
│   │    └── solvers      # various integer programming solvers...
│   │        ├── implicit_enumeration.py  # TODO: implicit enumeration solver for boolean programming
│   │        └── linear_relaxation.py     # TODO: linear relaxation solver for integer programming
│   ├── knapsack  # folder with knapsack related code
│   │    ├── ...  # various knapsack related classes
│   │    └── solvers # folder with knapsack solvers
│   │        ├── ... # various already implemented solvers
│   │        ├── integer_implicit_enumeration.py # TODO: use implicit enumeration to solve the knapsack problem
│   │        └── integer_linear_relaxation.py # TODO: use linear relaxation to solve the knapsack problem
│   └── simplex # folder with simplex implementation      
└── tests # pytest unit tests
```