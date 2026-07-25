from ..DiffusionModel import DiffusionModel
import numpy as np
import future.utils

__author__ = "Antigravity"
__license__ = "BSD-2-Clause"


class SAIRModel(DiffusionModel):
    """
    Model Parameters to be specified via ModelConfig:
    :param beta: The infection rate by symptomatic nodes (float value in [0,1])
    :param beta_a: The infection rate by asymptomatic nodes (float value in [0,1])
    :param p: The probability of showing symptoms (float value in [0,1])
    :param gamma_i: The recovery rate for symptomatic nodes (float value in [0,1])
    :param gamma_a: The recovery rate for asymptomatic nodes (float value in [0,1])
    """

    def __init__(self, graph, seed=None):
        super(self.__class__, self).__init__(graph, seed)
        self.available_statuses = {"Susceptible": 0, "Asymptomatic": 1, "Infected": 2, "Removed": 3}

        self.parameters = {
            "model": {
                "beta": {"descr": "Infection rate by symptomatic", "range": [0, 1], "optional": False},
                "beta_a": {"descr": "Infection rate by asymptomatic", "range": [0, 1], "optional": False},
                "p": {"descr": "Symptomatic probability", "range": [0, 1], "optional": False},
                "gamma_i": {"descr": "Symptomatic recovery rate", "range": [0, 1], "optional": False},
                "gamma_a": {"descr": "Asymptomatic recovery rate", "range": [0, 1], "optional": False},
            },
            "nodes": {},
            "edges": {},
        }

        self.active = []
        self.name = "SAIR"

    def iteration(self, node_status=True):
        """
        Execute a single model iteration
        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        self.clean_initial_status(self.available_statuses.values())

        actual_status = {
            node: nstatus for node, nstatus in future.utils.iteritems(self.status)
        }
        self.active = [
            node
            for node, nstatus in future.utils.iteritems(self.status)
            if nstatus != self.available_statuses["Susceptible"]
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

        # Keep track of newly infected nodes in this iteration to avoid double infection
        infected_nodes = set()

        for u in self.active:
            u_status = self.status[u]

            if u_status in [1, 2]:
                # Infection phase
                if self.graph.directed:
                    susceptible_neighbors = [
                        v for v in self.graph.successors(u) if self.status[v] == 0
                    ]
                else:
                    susceptible_neighbors = [
                        v for v in self.graph.neighbors(u) if self.status[v] == 0
                    ]

                beta = self.params["model"]["beta"] if u_status == 2 else self.params["model"]["beta_a"]

                for v in susceptible_neighbors:
                    if v not in infected_nodes:
                        eventp = np.random.random_sample()
                        if eventp < beta:
                            infected_nodes.add(v)
                            # Determine if symptomatic (2) or asymptomatic (1)
                            sym_p = np.random.random_sample()
                            if sym_p < self.params["model"]["p"]:
                                actual_status[v] = 2
                            else:
                                actual_status[v] = 1

                # Recovery phase
                eventp = np.random.random_sample()
                gamma = self.params["model"]["gamma_i"] if u_status == 2 else self.params["model"]["gamma_a"]
                if eventp < gamma:
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
