from ndlib.models.compartments.Compartment import Compartiment, ConfigurationException

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class NodeThreshold(Compartiment):

    def __init__(self, threshold=None, triggering_status=None, **kwargs):
        super(self.__class__, self).__init__(kwargs)
        self.threshold = threshold
        self.trigger = triggering_status

    def execute(self, node, graph, status, status_map, params, *args, **kwargs):
        neighbors = list(graph.neighbors(node))
        test = False

        try:
            directed = graph.directed
        except AttributeError:
            directed = graph.is_directed()

        if directed:
            neighbors = list(graph.predecessors(node))

        if self.trigger is None:
            triggered = 0
        else:
            triggered = len([v for v in neighbors if status[v] == status_map[self.trigger]])

        if len(list(neighbors)) > 0:
            infected_ratio = float(triggered) / len(neighbors)
            if 'threshold' in params['nodes']:
                test = infected_ratio >= params['nodes']['threshold'][node]
            else:
                if self.threshold is not None:
                    test = infected_ratio >= self.threshold
                else:
                    raise ConfigurationException("Threshold not specified")
        if test:
            return self.compose(node, graph, status, status_map, params, kwargs)

        return False
