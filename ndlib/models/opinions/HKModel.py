from ndlib.models.DiffusionModel import DiffusionModel
import future.utils
import numpy as np
import random
from sklearn.metrics import jaccard_score

__author__ = ['Letizia Milli']
__license__ = "BSD-2-Clause"

class HKModel(DiffusionModel):
    """
    Model Parameters to be specified via ModelConfig
    :param epsilon: bounded confidence threshold from the HK model (float in [0,1])
    """

    def __init__(self, graph):
        """
        Model Constructor
        :param graph: A networkx graph object
        """
        super(self.__class__, self).__init__(graph)
        self.discrete_state = False

        self.available_statuses = {
            "Infected": 0
        }

        self.parameters = {
            "model": {
                "epsilon": {
                    "descr": "Bounded confidence threshold",
                    "range": [0, 1],
                    "optional": False,
                }
            },
            "edges": {},
            "nodes": {},
        }
        self.name = "Hegselmann-Krause"

    def set_initial_status(self, configuration=None):
        """
        Override behaviour of methods in class DiffusionModel.
        Overwrites initial status using random real values.
        """
        super(HKModel, self).set_initial_status(configuration)

        # set node status
        for node in self.status:
            self.status[node] = random.uniform(-1, 1)
        self.initial_status = self.status.copy()


    def clean_initial_status(self, valid_status=None):
        for n, s in future.utils.iteritems(self.status):
            if s > 1 or s < -1:
                self.status[n] = 0.0

    def iteration(self, node_status=True):

        '''
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary code -> status)
        '''
        # An iteration changes the opinion of the selected agent 'i' .

        self.clean_initial_status(None)

        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(self.status)
            if node_status:
                return {"iteration": 0, "status": self.status.copy(),
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": 0, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}


        for i in range(0, self.graph.number_of_nodes()):
            # select a random node
            n1 = list(self.graph.nodes)[np.random.randint(0, self.graph.number_of_nodes())]

            # select neighbors of n1
            neighbours = list(self.graph.neighbors(n1))
            sum_op = 0
            count_in_eps = 0

            if len(neighbours) == 0:
                continue

            for neigh in neighbours:
                # compute the difference between opinions
                diff_opinion = np.abs((actual_status[n1]) - (actual_status[neigh]))
                if diff_opinion < self.params['model']['epsilon']:
                    sum_op += actual_status[neigh]
                    # count_in_eps is the number of neighbors in epsilon
                    count_in_eps += 1

            if (count_in_eps > 0):
                new_op = sum_op / float(count_in_eps)
            else:
                # if there aren't neighbors in epsilon, the status of n1 doesn't change
                new_op = actual_status[n1]

        actual_status[n1] = new_op

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1
        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(), "node_count": node_count.copy(),
                    "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {}, "node_count": node_count.copy(),
                    "status_delta": status_delta.copy()}
