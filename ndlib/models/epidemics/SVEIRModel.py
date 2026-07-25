from ..DiffusionModel import DiffusionModel
import numpy as np
import future.utils

__author__ = "Antigravity"
__license__ = "BSD-2-Clause"


class SVEIRModel(DiffusionModel):
    """
    Model Parameters to be specified via ModelConfig:
    :param beta: The infection rate (float value in [0,1])
    :param theta: The vaccination rate (float value in [0,1])
    :param sigma: The vaccine leakage / susceptibility multiplier (float value in [0,1])
    :param delta: The incubation rate (float value in [0,1])
    :param gamma: The recovery rate (float value in [0,1])
    """

    def __init__(self, graph, seed=None):
        super(self.__class__, self).__init__(graph, seed)
        self.available_statuses = {
            "Susceptible": 0,
            "Vaccinated": 1,
            "Exposed": 2,
            "Infected": 3,
            "Removed": 4
        }

        self.parameters = {
            "model": {
                "beta": {"descr": "Infection rate", "range": [0, 1], "optional": False},
                "theta": {"descr": "Vaccination rate", "range": [0, 1], "optional": False},
                "sigma": {"descr": "Vaccine leakage", "range": [0, 1], "optional": False},
                "delta": {"descr": "Incubation rate", "range": [0, 1], "optional": False},
                "gamma": {"descr": "Recovery rate", "range": [0, 1], "optional": False},
            },
            "nodes": {},
            "edges": {},
        }

        self.active = []
        self.name = "SVEIR"

    def iteration(self, node_status=True):
        """
        Execute a single model iteration
        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        self.clean_initial_status(self.available_statuses.values())

        actual_status = {
            node: nstatus for node, nstatus in future.utils.iteritems(self.status)
        }

        # In SVEIR, susceptible nodes are active because they can get vaccinated
        self.active = [
            node
            for node, nstatus in future.utils.iteritems(self.status)
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

        # Keep track of newly exposed nodes in this iteration
        exposed_nodes = set()

        for u in self.active:
            u_status = self.status[u]

            if u_status == 0:
                # Vaccination phase for susceptible nodes
                eventp = np.random.random_sample()
                if eventp < self.params["model"]["theta"]:
                    actual_status[u] = 1

            elif u_status == 3:
                # Infection phase from infected nodes to neighbors
                if self.graph.directed:
                    neighbors = list(self.graph.successors(u))
                else:
                    neighbors = list(self.graph.neighbors(u))

                beta = self.params["model"]["beta"]
                sigma = self.params["model"]["sigma"]

                for v in neighbors:
                    if v not in exposed_nodes:
                        v_status = self.status[v]
                        if v_status == 0:
                            eventp = np.random.random_sample()
                            if eventp < beta:
                                actual_status[v] = 2
                                exposed_nodes.add(v)
                        elif v_status == 1:
                            eventp = np.random.random_sample()
                            if eventp < sigma * beta:
                                actual_status[v] = 2
                                exposed_nodes.add(v)

                # Recovery phase for infected nodes
                eventp = np.random.random_sample()
                if eventp < self.params["model"]["gamma"]:
                    actual_status[u] = 4

            elif u_status == 2:
                # Incubation phase for exposed nodes
                eventp = np.random.random_sample()
                if eventp < self.params["model"]["delta"]:
                    actual_status[u] = 3

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
