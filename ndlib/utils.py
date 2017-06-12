import multiprocessing
import copy
import past

__author__ = 'Giulio Rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"


def multi_runs(model, execution_number=1, iteration_number=50):
    executions = []
    pool = multiprocessing.Pool()
    tasks = [copy.deepcopy(model).reset() for _ in past.builtins.xrange(0, execution_number)]
    results = [pool.apply_async(__execute, (t, iteration_number)) for t in tasks]

    for result in results:
        executions.append(result.get())

    return executions


def __execute(model, iteration_number):
    iterations = model.iteration_bunch(iteration_number, False)
    trends = model.build_trends(iterations)[0]
    return trends



