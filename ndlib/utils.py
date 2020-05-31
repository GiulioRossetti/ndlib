import numpy as np
import multiprocessing
from contextlib import closing
import copy
import past

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class InitializationException(Exception):
    """Initialization Exception"""


def multi_runs(model, execution_number=1, iteration_number=50, infection_sets=None,
               nprocesses=multiprocessing.cpu_count()):
    """
    Multiple executions of a given model varying the initial set of infected nodes

    :param model: a configured diffusion model
    :param execution_number: number of instantiations
    :param iteration_number: number of iterations per execution
    :param infection_sets: predefined set of infected nodes sets
    :param nprocesses: number of processes. Default values cpu number.
    :return: resulting trends for all the executions
    """

    if nprocesses > multiprocessing.cpu_count():
        nprocesses = multiprocessing.cpu_count()

    executions = []
    seeds = np.around(np.random.rand(execution_number)*2**32).astype(int)

    if infection_sets is not None:
        if len(infection_sets) != execution_number:
            raise InitializationException(
                {"message": "Number of infection sets provided does not match the number of executions required"})

        for x in past.builtins.xrange(0, execution_number, nprocesses):

            with closing(multiprocessing.Pool(processes=nprocesses, maxtasksperchild=10)) as pool:
                tasks = [(seeds[i], copy.deepcopy(model).reset(infection_sets[i])) for i in
                         past.builtins.xrange(x, min(x + nprocesses, execution_number))]
                results = [pool.apply_async(__execute, (*t, iteration_number)) for t in tasks]

            for result in results:
                executions.append(result.get())
    else:
        for x in past.builtins.xrange(0, execution_number, nprocesses):
            with closing(multiprocessing.Pool(processes=nprocesses, maxtasksperchild=10)) as pool:

                tasks = [(seeds[i], copy.deepcopy(model).reset()) for i in
                         past.builtins.xrange(x, min(x + nprocesses, execution_number))]
                results = [pool.apply_async(__execute, (*t, iteration_number)) for t in tasks]

            for result in results:
                executions.append(result.get())

    return executions


def __execute(seed, model, iteration_number):
    """
    Execute a simulation model

    :param model: a configured diffusion model
    :param iteration_number: number of iterations
    :return: computed trends
    """
    np.random.seed(seed)
    iterations = model.iteration_bunch(iteration_number, False)
    trends = model.build_trends(iterations)[0]
    del iterations
    del model
    return trends



