from ndlib.models.DiffusionModel import DiffusionModel
import numpy as np
import future.utils

__author__ = 'Letizia Milli'
__license__ = "BSD-2-Clause"
__email__ = "milli@di.unipi.it"


class ICEPModel(DiffusionModel):
    """
        Edge Parameters to be specified via ModelConfig

        :param permeability: The degree of permeability of a community toward outgoing diffusion processes
    """

    def __init__(self, graph):
        """
             Model Constructor

             :param graph: A networkx graph object
         """
        super(self.__class__, self).__init__(graph)
        self.available_statuses = {
            "Susceptible": 0,
            "Infected": 1,
            "Removed": 2
        }

        self.parameters = {
            "model": {
                "permeability":{
                    "descr": "Community permeability",
                    "range": [0,1],
                    "optional": False,
                    "default": 0.5
                }
            },
            "nodes": {},
            "edges": {
                "threshold": {
                    "descr": "Edge threshold",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.1}
            },
        }

        self.name = "Community Permeability"

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
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

        edge_embeddedness = {}
        for u in self.graph.nodes:
            if self.status[u] != 1:
                continue

            edge_embeddedness[u] = {}

            neighbors = list(self.graph.neighbors(u))  # neighbors and successors (in DiGraph) produce the same result


              # Standard threshold
            if len(neighbors) > 0:
                threshold = 1.0/len(neighbors)

                for v in neighbors:
                    if actual_status[v] == 0:
                        key = (u, v)

                        same_community_neighbors = 0
                        neighbors_v = list(self.graph.neighbors(v))
                        for neighbor in neighbors_v:
                            if neighbor in neighbors and self.params['nodes']['com'][neighbor] == self.params['nodes']['com'][u]:
                                same_community_neighbors += 1
                        edge_embeddedness[u][v] = float(same_community_neighbors) / float(
                            len(neighbors) + len(neighbors_v) - same_community_neighbors)

                        if self.params['nodes']['com'][u] == self.params['nodes']['com'][v]:  # within same community
                            threshold = edge_embeddedness[u][v]  # Embedness

                        else:  # across communities
                            p = self.params['model']['permeability']
                            if 'threshold' in self.params['edges']:
                                if key in self.params['edges']['threshold']:
                                    threshold = self.params['edges']['threshold'][key] * p
                                elif (v, u) in self.params['edges']['threshold'] and not self.graph.directed:
                                    threshold = self.params['edges']['threshold'][(v, u)] * p

                        flip = np.random.random_sample()
                        if flip <= threshold:
                            actual_status[v] = 1

            actual_status[u] = 2

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
