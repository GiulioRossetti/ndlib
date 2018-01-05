from ndlib.models.compartments.Compartment import Compartiment
import networkx as nx
import numpy as np

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class NodeCategoricalAttribute(Compartiment):

    def __init__(self, attribute, value, probability=1, **kwargs):
        super(self.__class__, self).__init__(kwargs)

        if not isinstance(value, str):
            raise ValueError("Categorical (string) value expected")

        self.attribute = attribute
        self.attribute_value = value
        self.probability = probability

    def execute(self, node, graph, status, status_map, *args, **kwargs):

        val = nx.get_node_attributes(graph, self.attribute)[node]
        p = np.random.random_sample()
        test = val == self.attribute_value and p <= self.probability

        if test:
            return self.compose(node, graph, status, status_map, kwargs)

        return False
