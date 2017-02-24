from DiffusionModel import DiffusionModel
import numpy as np

__author__ = 'Giulio Rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"


class IndependentCascadesModel(DiffusionModel):
    """
    Implements the independent cascade model by Kempe et al.
    Model parameters:
    (1) edge thresholds
    """

    def iteration(self):
        self.clean_initial_status([0, 1, 2])
        actual_status = {node: nstatus for node, nstatus in self.status.iteritems()}

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            return self.actual_iteration, actual_status

        for u in self.graph.nodes():
            if actual_status[u] != 1:
                continue

            neighbors = self.graph.neighbors(u)  # neighbors and successors (in DiGraph) produce the same result

            if len(neighbors) > 0:
                threshold = 1.0/len(neighbors)

                for v in neighbors:
                    if actual_status[v] == 0:
                        key = (u, v)
                        if key in self.params['edges']:
                            threshold = self.params['edges'][key]
                        flip = np.random.random_sample()
                        if flip <= threshold:
                            actual_status[v] = 1

            actual_status[u] = 2

        delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        return self.actual_iteration - 1, delta
