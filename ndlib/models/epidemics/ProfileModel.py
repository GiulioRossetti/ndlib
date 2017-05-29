from ..DiffusionModel import DiffusionModel
import networkx as nx
import numpy as np
import future.utils

__author__ = "Giulio Rossetti"
__email__ = "giulio.rossetti@gmail.com"


class ProfileModel(DiffusionModel):
    """
         Node Parameters to be specified via ModelConfig

        :param profile: The node profile. As default a value of 0.1 is assumed for all nodes.
     """

    def __init__(self, graph):
        """
        Model Constructor

        :param graph: A networkx graph object
        """
        super(self.__class__, self).__init__(graph)
        self.available_statuses = {
            "Susceptible": 0,
            "Infected": 1
        }

        self.parameters = {
            "model": {},
            "nodes": {
                "profile": {
                    "descr": "Node profile",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.1
                }
            },
            "edges": {},
        }

        self.name = "Profile"

    def iteration(self):
        """
        Iteration step

        :return: tuple (iid, nts)
        """
        self.clean_initial_status(self.available_statuses.values())
        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

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
                    actual_status[u] = 1

        delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        return self.actual_iteration - 1, delta
