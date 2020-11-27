# TODO
# - Parallel execution
# - Add sensitivity analysis options

from SALib.sample import saltelli
from SALib.analyze import sobol
from ndlib.models.compartments.enums.SAType import SAType
import numpy as np


class ContinuousModelRunner(object):
    def __init__(self, ContinuousModel, config, node_status=True):
        self.model = ContinuousModel
        self.config = config
        self.node_status = node_status

    def run(self, N, iterations_list,  initial_statuses, constants_list=None):
        results = []

        n_iterations = len(iterations_list)
        n_initial_statuses = len(initial_statuses)

        if constants_list:
            n_constants = len(constants_list)

        for i in range(N):
            print('\nRunning simulation ' + str(i + 1) + '/' + str(N) + '\n')
            if constants_list:
                self.model.constants = constants_list[i % n_constants]
            self.model.set_initial_status(initial_statuses[i % n_initial_statuses], self.config)
            output = self.model.iteration_bunch(iterations_list[i % n_iterations], node_status=self.node_status)
            results.append(output)

        return results

    def analyze_sensitivity(self, sa_type, initial_status, bounds, n, iterations, second_order=True):
        """
        Compute the sensitivity indices for the constants of the model using sobol
        Samples are generated using a Saltelli sampler

        :param sa_type: SAType indicating the metric for the sensitivity analysis, possible values
        :param initial_status: a dictionary with as key a state and as value, a number or function indicating the intial value for this state
        :param bounds: a dictionary with a constant name as key and a tuple (lower bound, upper bound) as value
        :param n: integer indicating the n for the function: N∗(2D+2) which is used to determine the amount of samples
        :param iterations: amount of iterations to run the model per sample
        :param second_order: bool indicating whether to include second order indices

        :return: a Python dict mapping state to a dictionary with the keys "S1", "S2", "ST", "S1_conf", "S2_conf", and "ST_conf"
        """
        if not self.model.constants:
            raise Exception('Please add constants when initializing the model to perform sensitivity analysis on')
        if not isinstance(sa_type, SAType):
            raise ValueError('Please use a SAType enum value for sa_type')

        problem = {
            'num_vars': len(bounds.keys()),
            'names': [var for var in bounds.keys()],
            'bounds': [
                [lower, upper] for _, (lower, upper) in bounds.items()
            ]
        }

        param_values = saltelli.sample(problem, n, calc_second_order=second_order)

        outputs = []

        # Set the constants and run the model
        for i in range(len(param_values)):
            print('Running simulation ' + str(i + 1) + '/' + str(len(param_values)))
            # Set the constants
            for j, name in enumerate(problem['names']):
                self.model.constants[name] = param_values[i,j]
            # Set intial values
            self.model.set_initial_status(initial_status, self.config)
            outputs.append(self.model.iteration_bunch(iterations, node_status=self.node_status, progress_bar=False))

        # Parse the outputs for every simulation (TODO: Optimize)
        print('Parsing outputs...')
        states = list(self.model.available_statuses.keys())
        states.remove('Infected')
        val_dict = {
            var: np.array([]) for var in states
        }
        values = self.parse_outputs(sa_type, outputs, val_dict)

        print('Running sensitivity analysis...')
        # Perform the sobol analysis seperately for every status
        analysis = {
            var: sobol.analyze(problem, values[var]) for var in states
        }

        return analysis

    def parse_outputs(self, sa_type, outputs, val_dict):
        mapping = {
            SAType.MEAN: self.mean_outputs
        }
        return mapping[sa_type](outputs, val_dict)

    def mean_outputs(self, outputs, val_dict):
        for output in outputs:
            # Get the average value of all the nodes for every status at the last iteration of the simulation
            means = self.model.get_means(output)
            for status in val_dict.keys():
                val_dict[status] = np.append(val_dict[status], means[status][-1])
        return val_dict

    def variance_outputs(self, outputs, val_dict):
        for output in outputs:
            # Get the average value of all the nodes for every status at the last iteration of the simulation
            means = self.model.get_means(output)
            for status in val_dict.keys():
                val_dict[status] = np.append(val_dict[status], means[status][-1])
        return val_dict