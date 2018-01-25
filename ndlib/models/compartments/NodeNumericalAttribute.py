from ndlib.models.compartments.Compartment import Compartiment
import networkx as nx
import numpy as np
import operator

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class NodeNumericalAttribute(Compartiment):

    def __init__(self, attribute, value=None, op=None, probability=1, **kwargs):
        super(self.__class__, self).__init__(kwargs)
        self.__available_operators = {"==": operator.__eq__, "<": operator.__lt__,
                                      ">": operator.__gt__, "<=": operator.__le__,
                                      ">=": operator.__ge__, "!=": operator.__ne__,
                                      "IN": (operator.__ge__, operator.__le__)}

        self.attribute = attribute
        self.attribute_range = value
        self.probability = probability
        self.operator = op

        if self.attribute_range is None:
            raise ValueError("A valid attribute value must be provided")

        if self.operator is not None and self.operator in self.__available_operators:
            if self.operator == "IN":
                if not isinstance(self.attribute_range, list) or self.attribute_range[1] < self.attribute_range[0]:
                    raise ValueError("A range list is required to test IN condition")
            else:
                if not isinstance(self.attribute_range, int):
                    if not isinstance(self.attribute_range, float):
                        raise ValueError("A numeric value is required to test the selected condition")
        else:
            raise ValueError("The operator provided '%s' is not valid" % operator)

    def execute(self, node, graph, status, status_map, *args, **kwargs):

        val = nx.get_node_attributes(graph, self.attribute)[node]
        p = np.random.random_sample()

        if self.operator == "IN":
            condition = self.__available_operators[self.operator][0](val, self.attribute_range[0]) and \
                        self.__available_operators[self.operator][1](val, self.attribute_range[1])
        else:
            condition = self.__available_operators[self.operator](val, self.attribute_range)

        test = condition and p <= self.probability

        if test:
            return self.compose(node, graph, status, status_map, kwargs)

        return False
