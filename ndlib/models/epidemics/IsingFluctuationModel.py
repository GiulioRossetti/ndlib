from ..DiffusionModel import DiffusionModel
import numpy as np
import networkx as nx
import future.utils
import random

__author__ = "Giulio Rossetti"
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class IFModel(DiffusionModel):
    """
    Model Parameters to be specified via ModelConfig

    :param beta: The infection rate (float value in [0,1])
    """

    def __init__(self, graph):
        """
             Model Constructor

             :param graph: A networkx graph object
         """
        super(self.__class__, self).__init__(graph)
        self.available_statuses = {
            "1": 1,
            "-1": -1,
            "Infected": 0
        }

        self.parameters = {
            "model": {
                "N1": {
                    "descr": "Node 1 id",
                    "optional": False},
                "N2": {
                    "descr": "Node 2 id",
                    "optional": False},
                "T1": {
                    "descr": "Temperature node 1",
                    "range": "[-1,1]",
                    "optional": False},
                "T2": {
                    "descr": "Temperature node 2",
                    "range": "[-1,1]",
                    "optional": False}
            },
            "nodes": {},
            "edges": {},
        }

        self.name = "IF"

    def __change_status(self, u, actual_status):

        neighbors = self.graph.neighbors(u)
        if isinstance(self.graph, nx.DiGraph):
            neighbors = self.graph.predecessors(u)

        s_u = 0
        s_u_inv = 0
        for n in neighbors:
            s_u += actual_status[u] * actual_status[n]
            s_u_inv += (-1 * actual_status[u]) * actual_status[n]

        if u != self.params['model']['N1'] and u != self.params['model']['N2']:
            if s_u == s_u_inv:
                flip = random.randint(0, 1)
                if flip == 1:
                    return True
                return False

        dif = s_u_inv - s_u
        if u == self.params['model']['N1']:
            dif /= self.params['model']['T1']
        else:
            dif /=  self.params['model']['T2']

        if s_u_inv < s_u:
            return True
        else:
            r = np.random.uniform(0, 1)
            if r < np.e**dif:
                return True
        return False

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        self.clean_initial_status(self.available_statuses.values())

        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(actual_status)
            if node_status:
                return {"iteration": 0, "status": actual_status.copy(),
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": 0, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}

        for u in self.graph.nodes():
            change = self.__change_status(u, actual_status)
            if change:
                actual_status[u] = -1*actual_status[u]


        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}

