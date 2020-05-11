from ndlib.models.compartments.Compartment import Compartiment
import networkx as nx
import numpy as np

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class EdgeCategoricalAttribute(Compartiment):

    def __init__(self, attribute, value, triggering_status=None, probability=1, **kwargs):
        super(self.__class__, self).__init__(kwargs)
        self.attribute = attribute

        if not isinstance(value, str):
            raise ValueError("Categorical (string) value expected")

        self.attribute_value = value
        self.trigger = triggering_status
        self.probability = probability

    def execute(self, node, graph, status, status_map, *args, **kwargs):
        neighbors = list(graph.neighbors(node))
        if isinstance(graph, nx.DiGraph):
            neighbors = list(graph.predecessors(node))

        edge_attr = graph.get_edge_attributes(self.attribute)

        if self.trigger is not None:
            triggered = [v for v in neighbors if status[v] == status_map[self.trigger] and
                         edge_attr[(min([node, v]), max([node, v]))] == self.attribute_value]
        else:
            triggered = [v for v in neighbors if edge_attr[(min([node, v]), max([node, v]))] == self.attribute_value]

        for _ in triggered:
            p = np.random.random_sample()
            test = p <= self.probability
            if test:
                return self.compose(node, graph, status, status_map, kwargs)

        return False
