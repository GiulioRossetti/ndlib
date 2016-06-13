from DiffusionModel import DiffusionModel
import numpy as np
import networkx as nx

__author__ = "Giulio Rossetti"
__email__ = "giulio.rossetti@gmail.com"


class SIRModel(DiffusionModel):
    """

    """

    def iteration(self):
        """

        """
        actual_status = {node: nstatus for node, nstatus in self.status.iteritems()}

        for u in self.graph.nodes():

            u_status = self.status[u]
            eventp = np.random.random_sample()
            neighbors = self.graph.neighbors(u)
            if isinstance(self.graph, nx.DiGraph):
                neighbors = self.graph.predecessors(u)

            if u_status == 0:
                infected_neighbors = len([v for v in neighbors if self.status[v] == 1])
                if eventp < self.params['beta'] * infected_neighbors:
                    actual_status[u] = 1
            elif u_status == 1:
                if eventp < self.params['gamma']:
                    actual_status[u] = 2

        self.status = actual_status
        self.actual_iteration += 1

        return self.actual_iteration, actual_status
