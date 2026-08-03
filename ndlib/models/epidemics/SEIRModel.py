from ..DiffusionModel import DiffusionModel
import numpy as np
import future

__author__ = ["Vincenzo Caproni", "Beatrice Caputo", "Ettore Puccetti", "Elisa Salatti"]
__license__ = "BSD-2-Clause"


class SEIRModel(DiffusionModel):
    def __init__(self, graph, seed=None):

        super(self.__class__, self).__init__(graph, seed)

        self.name = "SEIR"

        self.available_statuses = {
            "Susceptible": 0,
            "Exposed": 2,
            "Infected": 1,
            "Removed": 3,
        }
        self.parameters = {
            "model": {
                "alpha": {
                    "descr": "Latent period (1/duration)",
                    "range": [0, 1],
                    "optional": False,
                },
                "beta": {"descr": "Infection rate", "range": [0, 1], "optional": False},
                "gamma": {"descr": "Recovery rate", "range": [0, 1], "optional": False},
                "tp_rate": {
                    "descr": "Whether if the infection rate depends on the number of infected neighbors",
                    "range": [0, 1],
                    "optional": True,
                    "default": 1,
                },
            },
            "nodes": {},
            "edges": {},
        }

    def iteration(self, node_status=True):
        self.clean_initial_status(self.available_statuses.values())

        actual_status = {
            node: nstatus for node, nstatus in future.utils.iteritems(self.status)
        }

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
        legacy = False
        if legacy:
            for u in self.graph.nodes:

                u_status = self.status[u]
                eventp = np.random.random_sample()
                neighbors = self.graph.neighbors(u)
                if self.graph.directed:
                    neighbors = self.graph.predecessors(u)

                if u_status == 0:  # Susceptible

                    infected_neighbors = [v for v in neighbors if self.status[v] == 1]
                    triggered = 1 if len(infected_neighbors) > 0 else 0

                    if self.params["model"]["tp_rate"] == 1:
                        if eventp < 1 - (1 - self.params["model"]["beta"]) ** len(
                            infected_neighbors
                        ):
                            actual_status[u] = 2  # Exposed
                    else:
                        if eventp < self.params["model"]["beta"] * triggered:
                            actual_status[u] = 2  # Exposed

                elif u_status == 2:

                    # apply prob. of infection, after (t - t_i)
                    if eventp < self.params["model"]["alpha"]:
                        actual_status[u] = 1  # Infected

                elif u_status == 1:
                    if eventp < self.params["model"]["gamma"]:
                        actual_status[u] = 3  # Removed
        else:

            has_weights = self.graph_has_weights
            beta = self.params["model"]["beta"]
            alpha = self.params["model"]["alpha"]
            gamma = self.params["model"]["gamma"]
            use_tp = self.params["model"]["tp_rate"] == 1
            actual_status = self.status.copy()  # Assuming `actual_status` starts as a copy of `self.status`.

            # Pre-fetch edge weights if needed
            all_weights = self.graph.get_edge_attributes("weight") if has_weights else None

            # Precompute neighbors for all nodes
            if self.graph.directed:
                neighbors_dict = {u: list(self.graph.predecessors(u)) for u in self.graph.nodes}
            else:
                neighbors_dict = {u: list(self.graph.neighbors(u)) for u in self.graph.nodes}

            # Precompute random numbers for all nodes
            random_numbers = np.random.random_sample(len(self.graph.nodes))

            for idx, u in enumerate(self.graph.nodes):
                u_status = self.status[u]
                eventp = random_numbers[idx]

                if u_status == 0:  # Susceptible
                    # Get neighbors depending on graph type
                    neighbors = neighbors_dict[u]

                    # Find infected neighbors
                    infected_neighbors = [v for v in neighbors if self.status[v] == 1]
                    if not infected_neighbors:
                        continue  # Skip if no infected neighbors

                    # Compute infection probability
                    if use_tp:
                        if has_weights:
                            # Weighted sum of neighbor infections
                            total_weight = sum(all_weights.get((v, u), 1.0) for v in infected_neighbors)
                            infection_prob = 1 - (1 - beta) ** total_weight
                        else:
                            # Use count of infected neighbors
                            infection_prob = 1 - (1 - beta) ** len(infected_neighbors)
                    else:
                        infection_prob = beta

                    # Update to Exposed if infection occurs
                    if eventp < infection_prob:
                        actual_status[u] = 2  # Exposed

                elif u_status == 2:  # Exposed
                    # Check for progression to Infected
                    if eventp < alpha:
                        actual_status[u] = 1  # Infected

                elif u_status == 1:  # Infected
                    # Check for progression to Removed
                    if eventp < gamma:
                        actual_status[u] = 3  # Removed

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
