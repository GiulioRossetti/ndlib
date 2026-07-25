from ndlib.models.DiffusionModel import DiffusionModel
import future.utils
import numpy as np
import random

__author__ = "Antigravity"
__license__ = "BSD-2-Clause"


class FJModel(DiffusionModel):
    """
    Model Parameters to be specified via ModelConfig:
    :param init_dist_lower: The lower bound of the initial distribution (float)
    :param init_dist_upper: The upper bound of the initial distribution (float)
    :param stubbornness: Node stubbornness parameter (theta) (float in [0, 1])
    """

    def __init__(self, graph):
        """
        Model Constructor
        :param graph: A networkx graph object
        """
        super(self.__class__, self).__init__(graph)
        self.discrete_state = False
        self.available_statuses = {"Infected": 0}

        self.parameters = {
            "model": {
                "init_dist_lower": {
                    "descr": "The lower bound of the initial distribution",
                    "range": [-1, 1],
                    "optional": True,
                    "default": 0,
                },
                "init_dist_upper": {
                    "descr": "The upper bound of the initial distribution",
                    "range": [-1, 1],
                    "optional": True,
                    "default": 1,
                },
            },
            "edges": {},
            "nodes": {
                "stubbornness": {
                    "descr": "Node stubbornness parameter (theta)",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.1,
                }
            },
        }
        self.name = "Friedkin-Johnsen"

    def set_initial_status(self, configuration=None):
        """
        Override behavior of methods in class DiffusionModel.
        Overwrites initial status using random real values.
        """
        super(FJModel, self).set_initial_status(configuration)

        for node in self.status:
            self.status[node] = random.uniform(
                self.params["model"]["init_dist_lower"],
                self.params["model"]["init_dist_upper"]
            )
        self.initial_status = self.status.copy()

    def clean_initial_status(self, valid_status=None):
        for n, s in future.utils.iteritems(self.status):
            if s > 1 or s < -1:
                self.status[n] = 0.0

    def iteration(self, node_status=True):
        """
        Execute a single model iteration
        :return: Iteration_id, Incremental node status (dictionary node -> status)
        """
        self.clean_initial_status(None)

        actual_status = self.status.copy()
        new_status = {}

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

        for node in self.graph.nodes:
            # select neighbors
            neighbors = list(self.graph.neighbors(node))
            if self.graph.directed:
                neighbors = list(self.graph.predecessors(node))

            theta = 0.1
            if "stubbornness" in self.params["nodes"] and node in self.params["nodes"]["stubbornness"]:
                theta = self.params["nodes"]["stubbornness"][node]

            if len(neighbors) == 0:
                new_status[node] = actual_status[node]
            else:
                avg_opinion = np.mean([actual_status[neigh] for neigh in neighbors])
                new_status[node] = (1 - theta) * avg_opinion + theta * self.initial_status[node]

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
