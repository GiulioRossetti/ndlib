from DiffusionModel import DiffusionModel
import numpy as np
import networkx as nx

__author__ = "Giulio Rossetti"
__email__ = "giulio.rossetti@gmail.com"


class SISModel(DiffusionModel):
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
                if eventp < self.params['lambda']:
                    actual_status[u] = 0

        self.status = actual_status
        self.actual_iteration += 1

        return self.actual_iteration, actual_status

    def complete_run(self, max_iteration=200):
        system_status = []

        previous_status = {}

        confidence = 2
        count = 0

        while count < max_iteration:
            count += 1
            if confidence == 0:
                break

            itd, status = self.iteration()
            iteration = {"iteration": itd, "status": status}

            flag = self.check_status_similarity(status, previous_status)
            previous_status = status

            if flag:
                confidence -= 1

            system_status.append(iteration)

        return system_status
