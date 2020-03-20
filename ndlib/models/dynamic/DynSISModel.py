from ..DynamicDiffusionModel import DynamicDiffusionModel
import numpy as np
import networkx as nx
import future.utils

__author__ = "Giulio Rossetti"
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class DynSISModel(DynamicDiffusionModel):
    """
       Model Parameters to be specified via ModelConfig

       :param beta: The infection rate (float value in [0,1])
       :param lambda: The recovery rate (float value in [0,1])
    """

    def __init__(self, graph, seed=None):
        """
             Model Constructor

             :param graph: A networkx graph object
         """
        super(self.__class__, self).__init__(graph, seed)
        self.available_statuses = {
            "Susceptible": 0,
            "Infected": 1
        }

        self.parameters = {
            "model": {
                "beta": {
                    "descr": "Infection rate",
                    "range": [0, 1],
                    "optional": False},
                "lambda": {
                    "descr": "Recovery rate",
                    "range": [0, 1],
                    "optional": False
                }
            },
            "nodes": {},
            "edges": {},
        }

        self.name = "SIS"

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        self.clean_initial_status(self.available_statuses.values())

        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        # streaming
        if self.stream_execution:
            u, v = list(self.graph.edges())[0]
            u_status = self.status[u]
            v_status = self.status[v]

            # infection test
            if u_status == 1 and v_status == 0:
                p = np.random.random_sample()
                if p < self.params['model']['beta']:
                    actual_status[v] = 1

            if v_status == 1 and u_status == 0:
                p = np.random.random_sample()
                if p < self.params['model']['beta']:
                    actual_status[u] = 1

            # removal test
            if v_status == 1:
                g = np.random.random_sample()
                if g < self.params['model']['lambda']:
                    actual_status[v] = 0

            if u_status == 1:
                g = np.random.random_sample()
                if g < self.params['model']['lambda']:
                    actual_status[u] = 0

            delta, node_count, status_delta = self.status_delta(actual_status)
            self.status = actual_status
            self.actual_iteration += 1

            if node_status:
                return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": self.actual_iteration - 1, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        # snapshot
        else:

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

                u_status = self.status[u]
                eventp = np.random.random_sample()
                neighbors = self.graph.neighbors(u)
                if isinstance(self.graph, nx.DiGraph):
                    neighbors = self.graph.predecessors(u)

                if u_status == 0:
                    infected_neighbors = len([v for v in neighbors if self.status[v] == 1])
                    if eventp < self.params['model']['beta'] * infected_neighbors:
                        actual_status[u] = 1
                elif u_status == 1:
                    if eventp < self.params['model']['lambda']:
                        actual_status[u] = 0

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}

