from ..DiffusionModel import DiffusionModel
import numpy as np
import networkx as nx

__author__ = "Giulio Rossetti"
__email__ = "giulio.rossetti@gmail.com"


class ProfileThresholdModel(DiffusionModel):
    """
    Implement the Profile Threshold model of Milli et al.
    Model Parameters:
    (1) nodes profiles
    (2) nodes thresholds
    """

    def __init__(self, graph):
        super(self.__class__, self).__init__(graph)
        self.available_statuses = {
            "Susceptible": 0,
            "Infected": 1
        }

        self.parameters = {
            "model": {},
            "nodes": {
                "threshold": {
                    "descr": "Node threshold",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.1
                },
                "profile": {
                    "descr": "Node profile",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.1
                }
            },
            "edges": {},
        }

        self.name = "Profile-Threshold"

    def iteration(self):
        """

        """
        self.clean_initial_status(self.available_statuses.values())
        actual_status = {node: nstatus for node, nstatus in self.status.iteritems()}

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            return 0, actual_status

        for u in self.graph.nodes():
            if actual_status[u] == 1:
                continue

            neighbors = self.graph.neighbors(u)
            if isinstance(self.graph, nx.DiGraph):
                neighbors = self.graph.predecessors(u)

            infected = 0
            for v in neighbors:
                infected += self.status[v]

            if infected > 0:
                eventp = np.random.random_sample()
                if eventp >= self.params['nodes']['profile'][u]:
                    infected_ratio = float(infected)/len(neighbors)
                    if infected_ratio >= self.params['nodes']['threshold'][u]:
                        actual_status[u] = 1

        delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        return self.actual_iteration - 1, delta
