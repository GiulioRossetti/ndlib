from ndlib.models.DiffusionModel import DiffusionModel
import future.utils
import matplotlib.pyplot as plt
import copy
import numpy as np

__author__ = 'Mathijs Maijer'
__license__ = "BSD-2-Clause"
__email__ = "m.f.maijer@gmail.com"


class ContinuousModel(DiffusionModel):

    def __init__(self, graph, constants=None, clean_status=None):
        """
             Model Constructor
             :param graph: A networkx graph object
         """
        super(self.__class__, self).__init__(graph)
        self.compartment = {}
        self.compartment_progressive = 0
        self.status_progressive = 0

        self.discrete_state = False

        self.available_statuses = {
            "Infected": 0
        }

        self.clean = True if clean_status else False

        self.constants = constants

    def add_status(self, status_name):
        if status_name not in self.available_statuses:
            self.available_statuses[status_name] = self.status_progressive
            self.status_progressive += 1

    def add_rule(self, status, function, rule):
        self.compartment[self.compartment_progressive] = (status, function, rule)
        self.compartment_progressive += 1

    def set_initial_status(self, initial_status_funs, configuration=None):
        """
        Override behaviour of methods in class DiffusionModel.
        Overwrites initial status using given function
        Generates node profiles
        """
        super(ContinuousModel, self).set_initial_status(configuration)

        if not isinstance(initial_status_funs, dict):
            raise ValueError('The initial status should be a dictionary of form status (str): value (int/float/function)')

        # set node status
        for node in self.status:
            status = {}
            for status_fun in initial_status_funs.items():
                if hasattr(status_fun[1], '__call__'):
                    status[status_fun[0]] = status_fun[1](node, self.graph, status, self.constants)
                    continue
                if not isinstance(status_fun[1], float):
                    if not isinstance(status_fun[1], int):
                        raise ValueError('The initial status should be a function, integer, or float')
                status[status_fun[0]] = status_fun[1]
            self.status[node] = status

        self.initial_status = copy.deepcopy(self.status)

    def clean_initial_status(self, valid_status=None):
        for n, s in future.utils.iteritems(self.status):
            for var_val in s.items():
                if var_val[1] > 1:
                    self.status[n][var_val[0]] = 1
                elif var_val[1] < 0:
                    self.status[n][var_val[0]] = 0

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        if self.clean:
            self.clean_initial_status()

        # actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}
        actual_status = copy.deepcopy(self.status)

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, status_delta = self.status_delta_continuous(self.status)
            if node_status:
                return {"iteration": 0, "status": copy.deepcopy(self.status),
                        "status_delta": copy.deepcopy(status_delta)}
            else:
                return {"iteration": 0, "status": {},
                         "status_delta": copy.deepcopy(status_delta)}

        nodes_data = self.graph.nodes(data=True)

        for u in self.graph.nodes:

            # For all rules
            for i in range(0, self.compartment_progressive):
                # Get and test the condition
                rule = self.compartment[i][2]
                test = rule.execute(node=u, graph=self.graph, status=self.status,
                                    status_map=self.available_statuses, attributes=nodes_data,
                                    params=self.params, constants=self.constants)
                if test:
                    # Update status if test succeeds
                    val = self.compartment[i][1](u, self.graph, self.status, nodes_data, self.constants)
                    actual_status[u][self.compartment[i][0]] = val

        delta, status_delta = self.status_delta_continuous(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": copy.deepcopy(delta),
                    "status_delta": copy.deepcopy(status_delta)}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "status_delta": copy.deepcopy(status_delta)}

    def get_mean_data(self, iterations, mean_type):
        mean_changes = {}
        for key in self.available_statuses.keys():
            mean_changes[key] = []
        del mean_changes['Infected'] # Todo, fix this line so that infected isn't even in available statuses

        for it in iterations:
            delta = {}

            vals = list(it[mean_type].values())

            for val in vals:
                for key, v in val.items():
                    if key not in delta.keys():
                        delta[key] = {'v': v, 'n': 1}
                    else:
                        delta[key]['v'] += v
                        delta[key]['n'] += 1
            for key in mean_changes.keys():
                if key not in delta.keys():
                    delta[key] = {}
                    delta[key]['v'] = 0
                    delta[key]['n'] = 1

            for k, v in delta.items():
                if k not in mean_changes.keys():
                    mean_changes[k] = []
                mean_changes[k].append(delta[k]['v'] / delta[k]['n'])

        return mean_changes

    def build_full_status(self, iterations):
        statuses = []
        status = {'iteration': 0, 'status': {}}
        for key, val in iterations[0]['status'].items():
            status['status'][key] = val
        statuses.append(status)
        for it in iterations[1:]:
            i = it['iteration']
            status = copy.deepcopy(statuses[-1])
            for node, d in it['status'].items():
                for var, val in d.items():
                    status['status'][node][var] = val
                    status['iteration'] = i
            statuses.append(status)

        return statuses

    def get_means(self, iterations):
        full_status = self.build_full_status(iterations)
        means = self.get_mean_data(full_status, 'status')
        return means

    def build_trends(self, iterations):
        """
        Overwrite build trends of diffusionmodel
        """
        means = self.get_means(iterations)
        means_status_delta_vals = self.get_mean_data(iterations, 'status')
        status_delta = self.get_mean_data(iterations, 'status_delta')

        return {'mean_delta_status_vals': means_status_delta_vals, 'status_delta': status_delta, 'means': means}

    def visualize(self, trends, n, delta=None, delta_mean=None):
        x = np.arange(0, n)

        sub_plots = 1
        if delta:
            sub_plots = 2 if (delta and not delta_mean) else 3

        fig, axs = plt.subplots(sub_plots)

        # Mean status delta per iterations
        if delta or delta_mean: 
            for status, values in trends['means'].items():
                axs[0].plot(x, values, label=status)
            axs[0].set_title("Mean values per variable per iteration")
            axs[0].legend()
        else:
            for status, values in trends['means'].items():
                plt.plot(x, values, label=status)
            plt.title("Mean values per variable per iteration")
            plt.legend()


        if delta:
            for status, values in trends['status_delta'].items():
                axs[1].plot(x, values, label=status)
            axs[1].set_title("Mean change per variable per iteration")
            axs[1].legend()

        i = 2 if delta else 1

        if delta_mean:
            for status, values in trends['mean_delta_status_vals'].items():
                axs[i].plot(x, values, label=status)
            axs[i].set_title("Mean value of changed variables per iteration")
            axs[i].legend()

        plt.show()