from ndlib.models.compartments.Compartment import Compartiment
from ndlib.models.compartments.enums.NumericalType import NumericalType
import networkx as nx
import numpy as np
import operator

__author__ = 'Mathijs Maijer'
__license__ = "BSD-2-Clause"
__email__ = "m.f.maijer@gmail.com"


class NodeNumericalVariable(Compartiment):

    def __init__(self, var, var_type=None, value=None, value_type=None, op=None, probability=1, **kwargs):
        super(self.__class__, self).__init__(kwargs)
        self.__available_operators = {"==": operator.__eq__, "<": operator.__lt__,
                                      ">": operator.__gt__, "<=": operator.__le__,
                                      ">=": operator.__ge__, "!=": operator.__ne__,
                                      "IN": (operator.__ge__, operator.__le__)}

        self.variable = var
        self.variable_type = var_type
        self.value = value
        self.value_type = value_type
        self.probability = probability
        self.operator = op

        if not isinstance(self.variable, str):
            raise ValueError("The variable should be a string pointing to an attribute or status")
        if self.variable_type is None:
            raise ValueError("A type must be provided for the variable")
        if not isinstance(self.variable_type, NumericalType):
            raise ValueError("The provided variable type is not valid")
        if self.value_type and not isinstance(self.value_type, NumericalType):
            raise ValueError("The provided value type is not valid")
        if self.value is None:
            raise ValueError("A value must be provided")

        if self.operator is not None and self.operator in self.__available_operators:
            if self.operator == "IN":
                if not isinstance(self.value, list) or self.value[1] < self.value[0]:
                    raise ValueError("A range list is required to test IN condition")
            else:
                if self.value_type == None:
                    if not isinstance(self.value, int):
                        if not isinstance(self.value, float):
                            raise ValueError("When no value type is defined, the value should be numerical")
                else:
                    if not isinstance(self.value, str):
                        raise ValueError("The value should be a string pointing to an attribute or status when value type is set")
        else:
            raise ValueError("The operator provided '%s' is not valid" % operator)

    def execute(self, node, graph, status, status_map, attributes, *args, **kwargs):
        if self.variable_type == NumericalType.STATUS:
            val = status[node][self.variable]
        elif self.variable_type == NumericalType.ATTRIBUTE:
            val = attributes[node][self.variable]

        testVal = self.value

        if self.value_type == NumericalType.STATUS:
            testVal = status[node][self.value]
        elif self.value_type == NumericalType.ATTRIBUTE:
            testVal = attributes[node][self.value]

        p = np.random.random_sample()

        if self.operator == "IN":
            condition = self.__available_operators[self.operator][0](val, testVal[0]) and \
                        self.__available_operators[self.operator][1](val, testVal[1])
        else:
            condition = self.__available_operators[self.operator](val, testVal)

        test = condition and p <= self.probability

        if test:
            return self.compose(node, graph, status, status_map, kwargs)

        return False
