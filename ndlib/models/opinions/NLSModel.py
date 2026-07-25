from ..DiffusionModel import DiffusionModel
import networkx as nx

__author__ = "Antigravity"
__license__ = "BSD-2-Clause"


class NLSModel(DiffusionModel):
    """
    Model Parameters to be specified via ModelConfig:
    :param alpha: Distance decay exponent (float)
    :param strength: Node strength (persuasiveness) (float)
    :param threshold: Node threshold (resistance to change) (float)
    """

    def __init__(self, graph, seed=None):
        super(self.__class__, self).__init__(graph, seed)
        self.available_statuses = {"Susceptible": 0, "Infected": 1}

        self.parameters = {
            "model": {
                "alpha": {
                    "descr": "Distance decay exponent",
                    "range": [0, 10],
                    "optional": True,
                    "default": 2.0,
                }
            },
            "edges": {},
            "nodes": {
                "strength": {
                    "descr": "Node strength (persuasiveness)",
                    "range": [0, 100],
                    "optional": True,
                    "default": 1.0,
                },
                "threshold": {
                    "descr": "Node threshold (resistance to change)",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.0,
                }
            },
        }
        self.name = "Nowak-Lewenstein-Szamrej"
        self.distances = None

    def set_initial_status(self, configuration=None):
        """
        Override behavior of methods in class DiffusionModel.
        Computes all-pairs shortest paths for distance decay calculation.
        """
        super(NLSModel, self).set_initial_status(configuration)
        # Precompute all-pairs shortest path lengths depending on graph type
        if self.graph.tp == 0:
            self.distances = dict(nx.all_pairs_shortest_path_length(self.graph.graph))
        elif self.graph.tp == 1:
            g_ig = self.graph.graph
            names = g_ig.vs["name"]
            paths = g_ig.distances()
            self.distances = {}
            for i, src in enumerate(names):
                self.distances[src] = {}
                for j, dest in enumerate(names):
                    d = paths[i][j]
                    if d != float('inf'):
                        self.distances[src][dest] = d

    def iteration(self, node_status=True):
        """
        Execute a single model iteration (synchronous sweep)
        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        self.clean_initial_status(self.available_statuses.values())

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(self.status)
            if node_status:
                return {
                    "iteration": 0,
                    "status": self.status.copy(),
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

        actual_status = self.status.copy()
        new_status = {}
        alpha = self.params["model"]["alpha"]

        for node in self.graph.nodes:
            I_S = 0.0
            I_O = 0.0

            # Compute social impact from all other nodes in the network
            for j in self.graph.nodes:
                if j == node:
                    continue

                # Shortest path distance from j to node
                if node in self.distances[j]:
                    d = self.distances[j][node]
                    if d > 0:
                        strength = 1.0
                        if "strength" in self.params["nodes"] and j in self.params["nodes"]["strength"]:
                            strength = self.params["nodes"]["strength"][j]

                        impact = strength / (d ** alpha)

                        if actual_status[j] == actual_status[node]:
                            I_S += impact
                        else:
                            I_O += impact

            threshold = 0.0
            if "threshold" in self.params["nodes"] and node in self.params["nodes"]["threshold"]:
                threshold = self.params["nodes"]["threshold"][node]

            if (I_O - I_S) > threshold:
                new_status[node] = 1 - actual_status[node]
            else:
                new_status[node] = actual_status[node]

        delta, node_count, status_delta = self.status_delta(new_status)
        self.status = new_status
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
