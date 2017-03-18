from ..DiffusionModel import DiffusionModel
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

    def __init__(self, graph):
        super(self.__class__, self).__init__(graph)
        self.available_statuses = {
            "Susceptible": 0,
            "Infected": 1,
            "Removed": 2
        }

        self.parameters = {
            "model": {},
            "nodes": {},
            "edges": {
                "threshold": {
                    "descr": "Edge threshold",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.1
                }
            },
        }

        self.name = "Independent Cascades"

    def iteration(self):
        self.clean_initial_status(self.available_statuses.values())
        actual_status = {node: nstatus for node, nstatus in self.status.iteritems()}

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            return self.actual_iteration, actual_status

        for u in self.graph.nodes():
            if actual_status[u] != 1:
                continue

            neighbors = self.graph.neighbors(u)  # neighbors and successors (in DiGraph) produce the same result

            # Standard threshold
            if len(neighbors) > 0:
                threshold = 1.0/len(neighbors)

                for v in neighbors:
                    if actual_status[v] == 0:
                        key = (u, v)

                        # Individual specified thresholds
                        if 'threshold' in self.params['edges']:
                            if key in self.params['edges']['threshold']:
                                threshold = self.params['edges']['threshold'][key]

                        flip = np.random.random_sample()
                        if flip <= threshold:
                            actual_status[v] = 1

            actual_status[u] = 2

        delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        return self.actual_iteration - 1, delta
