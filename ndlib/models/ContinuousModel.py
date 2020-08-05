from ndlib.models.DiffusionModel import DiffusionModel
import future.utils
import copy

__author__ = 'Mathijs Maijer'
__license__ = "BSD-2-Clause"
__email__ = "m.f.maijer@gmail.com"


class ContinuousModel(DiffusionModel):

    def __init__(self, graph):
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

        # set node status
        for node in self.status:
            status = {}
            for status_fun in initial_status_funs.items():
                status[status_fun[0]] = status_fun[1](node, self.graph)
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
                                    params=self.params)
                if test:
                    # Update status if test succeeds
                    val = self.compartment[i][1](u, self.graph, self.status, nodes_data)
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
