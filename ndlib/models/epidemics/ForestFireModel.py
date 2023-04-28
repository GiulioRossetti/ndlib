import numpy as np

from ..DiffusionModel import DiffusionModel
import future.utils

__author__ = "Mavros Georgios"
__license__ = "BSD-2-Clause"
__email__ = "gmavros@protonmail.com"


class ForestFireModel(DiffusionModel):
    """
     Node Parameters to be specified via ModelConfig

    :param f: Probability with which a tree ignites, even if no neighbor is burning. (float value in [0,1])
    :param p: Probability with which an empty space fills with a tree .
    """

    def __init__(self, graph, seed=None):
        """
        Model Constructor

        :param graph: A networkx graph object
        """
        super(self.__class__, self).__init__(graph, seed)
        self.available_statuses = {
            "Susceptible": 0,  # Tree
            "Infected": 1,  # Burning Tree
            "Removed": 2,  # Empty Space
        }

        self.parameters = {
            "model": {
                "f": {"descr": "Ignite rate", "range": [0, 1], "optional": False},
                "p": {"descr": "Recovery rate", "range": [0, 1], "optional": False},
            },
            "nodes": {},
            "edges": {},
        }

        self.tree = []
        self.burn = []
        self.noTree = []
        self.name = "ForestFire"

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        self.clean_initial_status(self.available_statuses.values())

        actual_status = {
            node: nstatus for node, nstatus in future.utils.iteritems(self.status)
        }
        self.tree = [
            node
            for node, nstatus in future.utils.iteritems(self.status)
            if nstatus == self.available_statuses["Susceptible"]
        ]
        self.burn = [
            node
            for node, nstatus in future.utils.iteritems(self.status)
            if nstatus == self.available_statuses["Infected"]
        ]
        self.noTree = [
            node
            for node, nstatus in future.utils.iteritems(self.status)
            if nstatus == self.available_statuses["Removed"]
        ]

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(actual_status)
            if node_status:
                return {
                    "iteration": 0,
                    "status": actual_status.copy(),
                    "node_count": node_count.copy(),
                    "status_delta": status_delta.copy(),
                }
            else:
                return {
                    "iteration": 0,
                    "status": {},
                    "node_count": node_count.copy(),
                    "status_delta": status_delta.copy(),
                }

        for t in self.tree:
            if self.graph.directed:
                infected_neighbors = [
                    v for v in self.graph.successors(t) if self.status[v] == 1
                ]
            else:
                infected_neighbors = [
                    v for v in self.graph.neighbors(t) if self.status[v] == 1
                ]

            if len(infected_neighbors) >= 1:
                actual_status[t] = 1
            else:
                eventp = np.random.uniform(0.0, 1.0)
                if eventp < self.params["model"]["f"]:
                    actual_status[t] = 1

        for b in self.burn:
            actual_status[b] = 2

        for r in self.noTree:
            eventp = np.random.uniform(0.0, 1.0)
            if eventp < self.params["model"]["p"]:
                actual_status[r] = 0

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {
                "iteration": self.actual_iteration - 1,
                "status": delta.copy(),
                "node_count": node_count.copy(),
                "status_delta": status_delta.copy(),
            }
        else:
            return {
                "iteration": self.actual_iteration - 1,
                "status": {},
                "node_count": node_count.copy(),
                "status_delta": status_delta.copy(),
            }
