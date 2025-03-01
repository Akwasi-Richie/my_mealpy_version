# !/usr/bin/env python
# Created by "Thieu" at 11:59, 17/03/2020 ----------%
#       Email: nguyenthieu2102@gmail.com            %
#       Github: https://github.com/thieu1995        %
# --------------------------------------------------%

import numpy as np
from mealpy.optimizer import Optimizer


class BaseGWO(Optimizer):
    """
    The original version of: Grey Wolf Optimizer (GWO)

    Links:
        1. https://doi.org/10.1016/j.advengsoft.2013.12.007
        2. https://www.mathworks.com/matlabcentral/fileexchange/44974-grey-wolf-optimizer-gwo?s_tid=FX_rc3_behav

    Examples
    ~~~~~~~~
    >>> import numpy as np
    >>> from mealpy.swarm_based.GWO import BaseGWO
    >>>
    >>> def fitness_function(solution):
    >>>     return np.sum(solution**2)
    >>>
    >>> problem_dict1 = {
    >>>     "fit_func": fitness_function,
    >>>     "lb": [-10, -15, -4, -2, -8],
    >>>     "ub": [10, 15, 12, 8, 20],
    >>>     "minmax": "min",
    >>> }
    >>>
    >>> epoch = 1000
    >>> pop_size = 50
    >>> model = BaseGWO(problem_dict1, epoch, pop_size)
    >>> best_position, best_fitness = model.solve()
    >>> print(f"Solution: {best_position}, Fitness: {best_fitness}")

    References
    ~~~~~~~~~~
    [1] Mirjalili, S., Mirjalili, S.M. and Lewis, A., 2014. Grey wolf optimizer. Advances in engineering software, 69, pp.46-61.
    """

    def __init__(self, problem, epoch=10000, pop_size=100, **kwargs):
        """
        Args:
            problem (dict): The problem dictionary
            epoch (int): maximum number of iterations, default = 10000
            pop_size (int): number of population size, default = 100
        """
        super().__init__(problem, kwargs)
        self.epoch = self.validator.check_int("epoch", epoch, [1, 100000])
        self.pop_size = self.validator.check_int("pop_size", pop_size, [10, 10000])
        self.nfe_per_epoch = self.pop_size
        self.sort_flag = False

    def evolve(self, epoch):
        """
        The main operations (equations) of algorithm. Inherit from Optimizer class

        Args:
            epoch (int): The current iteration
        """
        # linearly decreased from 2 to 0
        a = 2 - 2 * epoch / (self.epoch - 1)
        _, list_best, _ = self.get_special_solutions(self.pop, best=3)

        pop_new = []
        for idx in range(0, self.pop_size):
            A1, A2, A3 = a * (2 * np.random.uniform() - 1), a * (2 * np.random.uniform() - 1), a * (2 * np.random.uniform() - 1)
            C1, C2, C3 = 2 * np.random.uniform(), 2 * np.random.uniform(), 2 * np.random.uniform()
            X1 = list_best[0][self.ID_POS] - A1 * np.abs(C1 * list_best[0][self.ID_POS] - self.pop[idx][self.ID_POS])
            X2 = list_best[1][self.ID_POS] - A2 * np.abs(C2 * list_best[1][self.ID_POS] - self.pop[idx][self.ID_POS])
            X3 = list_best[2][self.ID_POS] - A3 * np.abs(C3 * list_best[2][self.ID_POS] - self.pop[idx][self.ID_POS])
            pos_new = (X1 + X2 + X3) / 3.0
            pos_new = self.amend_position(pos_new, self.problem.lb, self.problem.ub)
            pop_new.append([pos_new, None])
            if self.mode not in self.AVAILABLE_MODES:
                target = self.get_target_wrapper(pos_new)
                self.pop[idx] = self.get_better_solution([pos_new, target], self.pop[idx])
        if self.mode in self.AVAILABLE_MODES:
            pop_new = self.update_target_wrapper_population(pop_new)
            self.pop = self.greedy_selection_population(self.pop, pop_new)


class RW_GWO(Optimizer):
    """
    The original version of: Random Walk Grey Wolf Optimizer (RW-GWO)

    Notes
    ~~~~~
    + This version is always performs worst than BaseGWO. Not sure why paper is accepted at Swarm and evolutionary computation

    Examples
    ~~~~~~~~
    >>> import numpy as np
    >>> from mealpy.swarm_based.GWO import RW_GWO
    >>>
    >>> def fitness_function(solution):
    >>>     return np.sum(solution**2)
    >>>
    >>> problem_dict1 = {
    >>>     "fit_func": fitness_function,
    >>>     "lb": [-10, -15, -4, -2, -8],
    >>>     "ub": [10, 15, 12, 8, 20],
    >>>     "minmax": "min",
    >>> }
    >>>
    >>> epoch = 1000
    >>> pop_size = 50
    >>> model = RW_GWO(problem_dict1, epoch, pop_size)
    >>> best_position, best_fitness = model.solve()
    >>> print(f"Solution: {best_position}, Fitness: {best_fitness}")

    References
    ~~~~~~~~~~
    [1] Gupta, S. and Deep, K., 2019. A novel random walk grey wolf optimizer. Swarm and evolutionary computation, 44, pp.101-112.
    """

    def __init__(self, problem, epoch=10000, pop_size=100, **kwargs):
        """
        Args:
            problem (dict): The problem dictionary
            epoch (int): maximum number of iterations, default = 10000
            pop_size (int): number of population size, default = 100
        """
        super().__init__(problem, kwargs)
        self.epoch = self.validator.check_int("epoch", epoch, [1, 100000])
        self.pop_size = self.validator.check_int("pop_size", pop_size, [10, 10000])
        self.nfe_per_epoch = self.pop_size + 3
        self.sort_flag = False

    def evolve(self, epoch):
        """
        The main operations (equations) of algorithm. Inherit from Optimizer class

        Args:
            epoch (int): The current iteration
        """
        # linearly decreased from 2 to 0, Eq. 5
        b = 2 - 2 * epoch / (self.epoch - 1)
        # linearly decreased from 2 to 0
        a = 2 - 2 * epoch / (self.epoch - 1)
        _, leaders, _ = self.get_special_solutions(self.pop, best=3)

        ## Random walk here
        leaders_new = []
        for i in range(0, len(leaders)):
            pos_new = leaders[i][self.ID_POS] + a * np.random.standard_cauchy(self.problem.n_dims)
            pos_new = self.amend_position(pos_new, self.problem.lb, self.problem.ub)
            leaders_new.append([pos_new, None])
            if self.mode not in self.AVAILABLE_MODES:
                target = self.get_target_wrapper(pos_new)
                leaders[i] = self.get_better_solution([pos_new, target], leaders[i])
        if self.mode in self.AVAILABLE_MODES:
            leaders_new = self.update_target_wrapper_population(leaders_new)
            leaders = self.greedy_selection_population(leaders, leaders_new)

        ## Update other wolfs
        pop_new = []
        for idx in range(0, self.pop_size):
            # Eq. 3
            miu1, miu2, miu3 = b * (2 * np.random.uniform() - 1), b * (2 * np.random.uniform() - 1), b * (2 * np.random.uniform() - 1)
            # Eq. 4
            c1, c2, c3 = 2 * np.random.uniform(), 2 * np.random.uniform(), 2 * np.random.uniform()
            X1 = leaders[0][self.ID_POS] - miu1 * np.abs(c1 * self.g_best[self.ID_POS] - self.pop[idx][self.ID_POS])
            X2 = leaders[1][self.ID_POS] - miu2 * np.abs(c2 * self.g_best[self.ID_POS] - self.pop[idx][self.ID_POS])
            X3 = leaders[2][self.ID_POS] - miu3 * np.abs(c3 * self.g_best[self.ID_POS] - self.pop[idx][self.ID_POS])
            pos_new = (X1 + X2 + X3) / 3.0
            pos_new = self.amend_position(pos_new, self.problem.lb, self.problem.ub)
            pop_new.append([pos_new, None])

            if self.mode not in self.AVAILABLE_MODES:
                target = self.get_target_wrapper(pos_new)
                self.pop[idx] = self.get_better_solution([pos_new, target], self.pop[idx])
        if self.mode in self.AVAILABLE_MODES:
            pop_new = self.update_target_wrapper_population(pop_new)
            self.pop = self.greedy_selection_population(self.pop, pop_new)
        self.pop = self.get_sorted_strim_population(self.pop + leaders, self.pop_size)
        
class GWO_WOA_M(Optimizer):
    """
    The original version of: The Proposed GWO-WOA

    Notes
    ~~~~~
    
    Examples
    ~~~~~~~~
    >>> import numpy as np
    >>> from mealpy.swarm_based.GWO import GWO_WOA_M
    >>>
    >>> def fitness_function(solution):
    >>>     return np.sum(solution**2)
    >>>
    >>> problem_dict2 = {
    >>>     "fit_func": fitness_function,
    >>>     "lb": [-10, -15, -4, -2, -8],
    >>>     "ub": [10, 15, 12, 8, 20],
    >>>     "minmax": "min",
    >>> }
    >>>
    >>> epoch = 1000
    >>> pop_size = 50
    >>> model = RW_GWO(problem_dict2, epoch, pop_size)
    >>> best_position, best_fitness = model.solve()
    >>> print(f"Solution: {best_position}, Fitness: {best_fitness}")
    
    References
    ~~~~~~~~~~
    [1] Mohammed, H. M., and Rashid, T. A., 2020. A novel hybrid GWO with WOA for Global Numerical 
    Optimization and Solving Pressure Vessel Design, Journal: Neural Computing and Applications, 2020, 
    44, pp.101-112.
    """
    def __init__(self, problem, epoch=10000, pop_size=100, **kwargs):
            """
            Args:
                problem (dict): The problem dictionary
                epoch (int): maximum number of iterations, default = 10000
                pop_size (int): number of population size, default = 100
            """
            super().__init__(problem, kwargs)
            self.epoch = self.validator.check_int("epoch", epoch, [1, 100000])
            self.pop_size = self.validator.check_int("pop_size", pop_size, [10, 10000])
            self.nfe_per_epoch = self.pop_size
            self.sort_flag = False
            
    def evolve(self, epoch):
            a = 2 - 2 * epoch / (self.epoch - 1)  # linearly decreased from 2 to 0
            a2 = -1 + epoch*((-1)/self.epoch-1)
            _, list_best, _ = self.get_special_solutions(self.pop, best=3)
            pop_new = []
            for idx in range(0, self.pop_size):
                r1 = np.random.rand()
                r2 = np.random.rand()
                A = 2 * a * r1 - a
                C = 2 * r2
                l = (a2 -1) + np.random.rand() +1
                p = np.random.rand()
                b = 1
                A1 = a * (2 * np.random.uniform() - 1)
                C1 = 2 * np.random.uniform()
                A2 = a * (2 * np.random.uniform() - 1)
                C2 = 2 * np.random.uniform()
                A3 = a * (2 * np.random.uniform() - 1)
                C3 = 2 * np.random.uniform()
                
                if p < 0.5:
                    if np.abs(A) < 1:
                        D = np.abs(C * self.g_best[self.ID_POS] - self.pop[idx][self.ID_POS])
                        pos_new = self.g_best[self.ID_POS] - A * D
                    else:
                        # x_rand = pop[np.random.np.random.randint(self.pop_size)]         # select random 1 position in pop
                        x_rand = self.create_solution(self.problem.lb, self.problem.ub)
                        D = np.abs(C * x_rand[self.ID_POS] - self.pop[idx][self.ID_POS])
                        pos_new = x_rand[self.ID_POS] - A * D
                else:
                    D1 = np.abs(C2 * list_best[0][self.ID_POS] - self.pop[idx][self.ID_POS])
                    X1 = list_best[0][self.ID_POS] - A1 * D1
                    
                    D2 = np.abs(C1 * list_best[1][self.ID_POS] - self.pop[idx][self.ID_POS])
                    X2 = list_best[1][self.ID_POS] - A2 * D2
                    
                    D3 = np.abs(C3 * list_best[2][self.ID_POS] - self.pop[idx][self.ID_POS])
                    X3 = list_best[2][self.ID_POS] - A3 * D3
                    
        
        
                    pos_new = (X1 + X2 + X3) / 3.0
                    pos_new = self.amend_position(pos_new, self.problem.lb, self.problem.ub)
                    pop_new.append([pos_new, None])
                    if self.mode not in self.AVAILABLE_MODES:
                       target = self.get_target_wrapper(pos_new)
                       self.pop[idx] = self.get_better_solution([pos_new, target], self.pop[idx])
                       
                if self.mode in self.AVAILABLE_MODES:
                    pop_new = self.update_target_wrapper_population(pop_new)
                    self.pop = self.greedy_selection_population(self.pop, pop_new)
                    
    
class GWO_WOA_O(Optimizer):
    """
    The original version of: The Proposed GWO-WOA

    Notes
    ~~~~~
    
    Examples
    ~~~~~~~~
    >>> import numpy as np
    >>> from mealpy.swarm_based.GWO import GWO_WOA_O
    >>>
    >>> def fitness_function(solution):
    >>>     return np.sum(solution**2)
    >>>
    >>> problem_dict2 = {
    >>>     "fit_func": fitness_function,
    >>>     "lb": [-10, -15, -4, -2, -8],
    >>>     "ub": [10, 15, 12, 8, 20],
    >>>     "minmax": "min",
    >>> }
    >>>
    >>> epoch = 1000
    >>> pop_size = 50
    >>> model = RW_GWO(problem_dict2, epoch, pop_size)
    >>> best_position, best_fitness = model.solve()
    >>> print(f"Solution: {best_position}, Fitness: {best_fitness}")
    
    References
    ~~~~~~~~~~
   [1] Obadina, O. 0., Thana, M. A. and Saheed, M. H., 2021. Dynamic 
   characterization of a master–slave robotic manipulator using a hybrid 
   grey wolf–whale optimization algorithm. Journal of Vibration and Control, 
   2021, Vol. 0(0), pp. 1–12.
    """
    def __init__(self, problem, epoch=10000, pop_size=100, **kwargs):
            """
            Args:
                problem (dict): The problem dictionary
                epoch (int): maximum number of iterations, default = 10000
                pop_size (int): number of population size, default = 100
            """
            super().__init__(problem, kwargs)
            self.epoch = self.validator.check_int("epoch", epoch, [1, 100000])
            self.pop_size = self.validator.check_int("pop_size", pop_size, [10, 10000])
            self.nfe_per_epoch = self.pop_size
            self.sort_flag = False
            
    def evolve(self, epoch):
            # a = 2 - 2 * epoch / (self.epoch - 1)  # linearly decreased from 2 to 0
            # a2 = -1 + epoch*((-1)/self.epoch-1)
            a = 2 * (1 - (epoch / (2 * (self.epoch))))
            _, list_best, _ = self.get_special_solutions(self.pop, best=3)
            pop_new = []
            for idx in range(0, self.pop_size):
                r1 = np.random.rand()
                r2 = np.random.rand()
                r3 = np.random.rand()
                A = 2 * a * r1 - a
                C = 2 * r2
                w = np.random.rand()
                # l = (a2 -1) + np.random.rand() +1
                l = np.random.uniform(-1, 1)
                p = np.random.rand()
                b = 1
                A1 = a * (2 * np.random.uniform() - 1)
                C1 = 2 * np.random.uniform()
                A2 = a * (2 * np.random.uniform() - 1)
                C2 = 2 * np.random.uniform()
                A3 = a * (2 * np.random.uniform() - 1)
                C3 = 2 * np.random.uniform()
                
                if p < 0.5:
                    if np.abs(A) < 1:
                        D = r3 * np.abs(C * self.g_best[self.ID_POS] - self.pop[idx][self.ID_POS])
                        pos_new = self.g_best[self.ID_POS] - A * D
                    else:
                        # x_rand = pop[np.random.np.random.randint(self.pop_size)]         # select random 1 position in pop
                        x_rand = self.create_solution(self.problem.lb, self.problem.ub)
                        D = (w * np.exp(b * l) * np.cos(2 * np.pi * l)) * (np.abs(C1 * list_best[0][self.ID_POS] - self.pop[idx][self.ID_POS]))
                        pos_new = x_rand[self.ID_POS] - A * D
                else:
                    D1 = np.abs(C2 * list_best[0][self.ID_POS] - self.pop[idx][self.ID_POS])
                    X1 = list_best[0][self.ID_POS] - A1 * D1
                    
                    D2 = np.abs(C1 * list_best[1][self.ID_POS] - self.pop[idx][self.ID_POS])
                    X2 = list_best[1][self.ID_POS] - A2 * D2
                    
                    D3 = np.abs(C3 * list_best[2][self.ID_POS] - self.pop[idx][self.ID_POS])
                    X3 = list_best[2][self.ID_POS] - A3 * D3
                    
        
        
                    pos_new = (X1 + X2 + X3) / 3.0
                    pos_new = self.amend_position(pos_new, self.problem.lb, self.problem.ub)
                    pop_new.append([pos_new, None])
                    if self.mode not in self.AVAILABLE_MODES:
                       target = self.get_target_wrapper(pos_new)
                       self.pop[idx] = self.get_better_solution([pos_new, target], self.pop[idx])
                       
                if self.mode in self.AVAILABLE_MODES:
                    pop_new = self.update_target_wrapper_population(pop_new)
                    self.pop = self.greedy_selection_population(self.pop, pop_new)
