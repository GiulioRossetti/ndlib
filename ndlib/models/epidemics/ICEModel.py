from ndlib.models.DiffusionModel import DiffusionModel
import numpy as np
import future.utils
import networkx as nx

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class ICEModel(DiffusionModel):
    """
        Parameter free model: probability of diffusion tied to community embeddedness of individual nodes
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
            "model": {},
            "nodes": {},
            "edges": {}
        }

        self.name = "Community Embeddedness"

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
            com_embeddedness = {}

            neighbors = list(self.graph.neighbors(u))  # neighbors and successors (in DiGraph) produce the same result
            embeddedness = 1
            for v in neighbors:
                same_community_neighbors = 0
                neighbors_v = list(self.graph.neighbors(v))
                for neighbor in neighbors_v:
                    if neighbor in neighbors and self.params['nodes']['com'][neighbor] == self.params['nodes']['com'][u]:
                        same_community_neighbors += 1
                tmp_embeddedness = float(same_community_neighbors) / float(
                    len(neighbors) + len(neighbors_v) - same_community_neighbors)
                edge_embeddedness[u][v] = tmp_embeddedness
                if tmp_embeddedness < embeddedness:
                    embeddedness = tmp_embeddedness
            com_embeddedness[self.params['nodes']['com'][u]] = embeddedness


           # neighbors = list(self.graph.neighbors(u))  # neighbors and successors (in DiGraph) produce the same result
            #same_community_neighbors = [n for n in neighbors if self.params['nodes']['com'][u] == self.params['nodes']['com'][n]]

            # Standard threshold
            if len(neighbors) > 0:

                for v in neighbors:
                    if actual_status[v] == 0:

                        if self.params['nodes']['com'][u] == self.params['nodes']['com'][v]:
                            threshold = edge_embeddedness[u][v]

                        else: # across communities
                            threshold = com_embeddedness[self.params['nodes']['com'][u]]

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
