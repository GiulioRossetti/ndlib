from ..DiffusionModel import DiffusionModel
import numpy as np
import future

__author__ = "Letizia Milli"
__license__ = "BSD-2-Clause"


class SWIRModel(DiffusionModel):

    def __init__(self, graph, seed=None):

        super(self.__class__, self).__init__(graph, seed)

        self.name = "SWIR"

        self.available_statuses = {
            "Susceptible": 0,
            "Weakened": 2,
            "Infected": 1,
            "Removed": 3
        }
        self.parameters = {
            "model": {
                "kappa": {
                    "descr": "Infection rate from susceptible state",
                    "range": [0, 1],
                    "optional": False},
                "mu": {
                    "descr": "Weakened rate",
                    "range": [0, 1],
                    "optional": False},
                "nu": {
                    "descr": "Infection rate from weakened state",
                    "range": [0, 1],
                    "optional": False
                }
            },
            "nodes": {},
            "edges": {},
        }

    def iteration(self, node_status=True):
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

        for u in self.graph.nodes:

            u_status = self.status[u]
            eventp = np.random.random_sample()
            neighbors = self.graph.neighbors(u)
            if self.graph.directed:
                neighbors = self.graph.predecessors(u)

            if u_status == 1:  # Infected
                for neighbor in neighbors:
                    if self.status[neighbor] == 0:  # Susceptible
                        if eventp < self.params['model']['kappa']:
                            actual_status[neighbor] = 1  # Infected
                        else:
                            eventp = np.random.random_sample()
                            if eventp < self.params['model']['mu']:
                                actual_status[neighbor] = 2  # Weakened
                    elif self.status[neighbor] == 2:  # Weakened
                        if eventp < self.params['model']['nu']:
                            actual_status[neighbor] = 1  # Infected
                actual_status[u] = 3  # Removed

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
