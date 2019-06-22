from ndlib.models.compartments.Compartment import Compartiment, ConfigurationException
import numpy as np

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class EdgeStochastic(Compartiment):

    def __init__(self, threshold=None, triggering_status=None, **kwargs):
        super(self.__class__, self).__init__(kwargs)
        self.threshold = threshold
        self.trigger = triggering_status
        if self.trigger is None:
            raise ConfigurationException("Triggering status not specified.")

    def execute(self, node, graph, status, status_map, params, *args, **kwargs):
        neighbors = list(graph.neighbors(node))

        try:
            directed = graph.directed
        except AttributeError:
            directed = graph.is_directed()

        if directed:
            neighbors = list(graph.predecessors(node))

        threshold = float(1)/len(neighbors)
        triggered = [v for v in neighbors if status[v] == status_map[self.trigger]]

        for n in triggered:
            if 'threshold' in params['edges']:
                key = (node, n)
                try:
                    threshold = params['edges']['threshold'][key]
                except KeyError:
                    threshold = params['edges']['threshold'][(n, node)]
            else:
                if self.threshold is not None:
                    threshold = self.threshold
            flip = np.random.random_sample()
            test = flip <= threshold

            if test:
                return self.compose(node, graph, status, status_map, params, kwargs)

        return False

