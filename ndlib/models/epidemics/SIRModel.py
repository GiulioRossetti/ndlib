from ..DiffusionModel import DiffusionModel
import numpy as np
import future.utils

__author__ = "Giulio Rossetti"
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class SIRModel(DiffusionModel):
    """
    Model Parameters to be specified via ModelConfig

    :param beta: The infection rate (float value in [0,1])
    :param gamma: The recovery rate (float value in [0,1])
    """

    def __init__(self, graph, seed=None):
        """
        Model Constructor

        :param graph: A networkx graph object
        """
        super(self.__class__, self).__init__(graph, seed)
        self.available_statuses = {"Susceptible": 0, "Infected": 1, "Removed": 2}

        self.parameters = {
            "model": {
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

        self.active = []
        self.name = "SIR"

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

        # Pre-fetch model parameters
        beta = self.params["model"]["beta"]
        gamma = self.params["model"]["gamma"]
        use_tp = self.params["model"]["tp_rate"] == 1
        has_weights = self.graph_has_weights
        actual_status = self.status.copy()

        # Pre-fetch edge weights if needed
        all_weights = self.graph.get_edge_attributes("weight") if has_weights else None

        # Precompute neighbors for all nodes
        if self.graph.directed:
            neighbors_dict = {u: list(self.graph.successors(u)) for u in self.graph.nodes}
        else:
            neighbors_dict = {u: list(self.graph.neighbors(u)) for u in self.graph.nodes}

        # Precompute random numbers for each susceptible neighbor and recovery events
        num_events = sum(len(neighbors_dict[u]) for u in self.active if self.status[u] == 1)
        random_numbers = np.random.random_sample(num_events + len(self.active))
        random_idx = 0  # Pointer to track random number usage

        # Process active infected nodes
        for u in self.active:
            if self.status[u] != 1:  # Skip non-infected nodes
                continue

            # Get precomputed neighbors
            neighbors = neighbors_dict[u]
            susceptible_neighbors = [v for v in neighbors if self.status[v] == 0]

            # Try to infect each susceptible neighbor
            for v in susceptible_neighbors:
                eventp = random_numbers[random_idx]  # Use precomputed random number
                random_idx += 1

                if use_tp and has_weights:
                    # Get edge weight
                    edge_weight = all_weights[(u, v)]  # Use (u, v) since u infects v
                    infection_prob = 1 - (1 - beta) ** edge_weight
                else:
                    infection_prob = beta  # Simple infection process

                if eventp < infection_prob:
                    actual_status[v] = 1

            # Check if infected node recovers
            recovery_event = random_numbers[random_idx]  # Use precomputed random number
            random_idx += 1

            if recovery_event < gamma:
                actual_status[u] = 2
    
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
