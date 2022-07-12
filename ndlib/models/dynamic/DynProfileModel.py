from ..DynamicDiffusionModel import DynamicDiffusionModel
import numpy as np
import networkx as nx
import future.utils
from scipy import stats

__author__ = "Letizia Milli"
__license__ = "BSD-2-Clause"
__email__ = "letizia.milli@isti.cnr.it"


class DynProfileModel(DynamicDiffusionModel):
    """
             Node Parameters to be specified via ModelConfig

            :param profile: The node profile. As default a value of 0.1 is assumed for all nodes.
         """

    def __init__(self, graph, seed=None):
        """
             Model Constructor

             :param graph: A networkx graph object
         """
        super(self.__class__, self).__init__(graph, seed)
        self.available_statuses = {
            "Susceptible": 0,
            "Infected": 1,
            "Blocked": -1
        }

        self.parameters = {
            "model": {
                "blocked": {
                    "descr": "Presence of blocked nodes",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
                "adopter_rate": {
                    "descr": "Exogenous adoption rate",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                }
            },
            "nodes": {
                "profile": {
                    "descr": "Node profile",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.1
                }
            },
            "edges": {},
        }

        self.name = "Profile"

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        self.clean_initial_status(self.available_statuses.values())
        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        # streaming
        if self.stream_execution:
            raise ValueError("Streaming network not allowed.")
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
                if actual_status[u] != 0:
                    continue

                if self.params['model']['adopter_rate'] > 0:
                    xk = (0, 1)
                    pk = (1 - self.params['model']['adopter_rate'], self.params['model']['adopter_rate'])
                    probability = stats.rv_discrete(name='probability', values=(xk, pk))
                    number_probability = probability.rvs()

                    if number_probability == 1:
                        actual_status[u] = 1
                        continue

                neighbors = self.graph.neighbors(u)
                if isinstance(self.graph, nx.DiGraph):
                    neighbors = self.graph.predecessors(u)

                infected = 0
                for v in neighbors:
                    infected += self.status[v]

                if infected > 0 and actual_status[u] == 0:
                    eventp = np.random.random_sample()
                    if eventp >= self.params['nodes']['profile'][u]:
                        actual_status[u] = 1
                    else:
                        if self.params['model']['blocked'] != 0:
                            blip = np.random.random_sample()
                            if blip > self.params['model']['blocked']:
                                actual_status[u] = -1

            delta, node_count, status_delta = self.status_delta(actual_status)
            self.status = actual_status
            self.actual_iteration += 1

            if node_status:
                return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": self.actual_iteration - 1, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
