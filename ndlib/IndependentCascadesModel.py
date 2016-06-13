from DiffusionModel import DiffusionModel
import numpy as np

__author__ = 'rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"


class IndependentCascadesModel(DiffusionModel):

    def iteration(self):
        actual_status = {node: nstatus for node, nstatus in self.status.iteritems()}

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

        self.status = actual_status
        self.actual_iteration += 1

        return self.actual_iteration, actual_status

        pass
