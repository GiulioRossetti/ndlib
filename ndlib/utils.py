import multiprocessing
from contextlib import closing
import copy
import past

__author__ = 'Giulio Rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"


def multi_runs(model, execution_number=1, iteration_number=50, infection_sets=None,
               nprocesses=multiprocessing.cpu_count()):

    if nprocesses > multiprocessing.cpu_count():
        nprocesses = multiprocessing.cpu_count()

    executions = []

    if infection_sets is not None:
        if len(infection_sets) != execution_number:
            raise Exception

        for x in past.builtins.xrange(0, execution_number, nprocesses):

            with closing(multiprocessing.Pool(processes=nprocesses, maxtasksperchild=10)) as pool:
                tasks = [copy.copy(model).reset(infection_sets[i]) for i in
                         past.builtins.xrange(x, min(x + nprocesses, execution_number))]
                results = [pool.apply_async(__execute, (t, iteration_number)) for t in tasks]

            for result in results:
                executions.append(result.get())
    else:
        for x in past.builtins.xrange(0, execution_number, nprocesses):
            with closing(multiprocessing.Pool(processes=nprocesses, maxtasksperchild=10)) as pool:

                tasks = [copy.deepcopy(model).reset() for _ in
                         past.builtins.xrange(x, min(x + nprocesses, execution_number))]
                results = [pool.apply_async(__execute, (t, iteration_number)) for t in tasks]

            for result in results:
                executions.append(result.get())

    return executions


def __execute(model, iteration_number):
    iterations = model.iteration_bunch(iteration_number, False)
    trends = model.build_trends(iterations)[0]
    del iterations
    del model
    return trends



