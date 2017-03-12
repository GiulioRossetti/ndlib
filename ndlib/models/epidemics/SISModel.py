from ..DiffusionModel import DiffusionModel
import numpy as np
import networkx as nx

__author__ = "Giulio Rossetti"
__email__ = "giulio.rossetti@gmail.com"


class SISModel(DiffusionModel):
    """
    Implement the SIR model of Kermack et al.
    Model Parameters:
    (1) the infection rate beta
    (2) the recovery rate lambda
    """

    def __init__(self, graph):
        super(self.__class__, self).__init__(graph)
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

    def iteration(self):
        """

        """
        self.clean_initial_status(self.available_statuses.values())

        actual_status = {node: nstatus for node, nstatus in self.status.iteritems()}

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            return 0, actual_status

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

        delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        return self.actual_iteration - 1, delta
