from ndlib.models.compartments.Compartment import Compartiment
import numpy as np
import networkx as nx

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class NodeStochastic(Compartiment):

    def __init__(self, rate, triggering_status=None, **kwargs):
        super(self.__class__, self).__init__(kwargs)
        self.rate = rate
        self.trigger = triggering_status

    def execute(self, node, graph, status, status_map, *args, **kwargs):
        neighbors = graph.neighbors(node)
        if isinstance(graph, nx.DiGraph):
            neighbors = graph.predecessors(node)

        p = np.random.random_sample()
        if self.trigger is None:
            triggered = 1
        else:
            triggered = len([v for v in neighbors if status[v] == status_map[self.trigger]])

        test = p < self.rate * triggered
        if test:
            return self.compose(node, graph, status, status_map, kwargs)

        return False
