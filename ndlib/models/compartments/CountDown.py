from ndlib.models.compartments.Compartment import Compartiment

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class CountDown(Compartiment):

    def __init__(self, name, iterations, **kwargs):
        super(self.__class__, self).__init__(kwargs)
        self.iterations = iterations
        self.name = name

    def execute(self, node, graph, status, status_map, *args, **kwargs):
        if self.name in graph.nodes[node]:
            graph.nodes[node][self.name] -= 1
        else:
            graph.nodes[node][self.name] = self.iterations

        test = graph.nodes[node][self.name] == 0
        if test:
            return self.compose(node, graph, status, status_map, kwargs)

        return False
