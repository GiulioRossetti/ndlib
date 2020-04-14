from ndlib.models.compartments.Compartment import Compartiment
import networkx as nx
import numpy as np
from scipy.sparse import csr_matrix

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
                    (edge_attr.get((node, v))==self.attribute_value or edge_attr.get((v, node))==self.attribute_value)] ## STEFANO: had to modify this bc edges were not sorted in my case
        else:
            triggered = [v for v in neighbors if edge_attr.get((node, v))==self.attribute_value or edge_attr.get((v, node))==self.attribute_value] ## STEFANO: had to modify this bc edges were not sorted in my case

        for _ in triggered:
            p = np.random.random_sample()
            test = p <= self.probability
            if test:
                return self.compose(node, graph, status, status_map, kwargs)

        return False


## STEFANO: NEW ARRAY BASED COMPARTMENT
class EdgeCategoricalAttributeArray(Compartiment):

    def __init__(self, attribute, value, triggering_status=None, probability=1, **kwargs):
        super(self.__class__, self).__init__(kwargs)
        self.attribute = attribute

        if not isinstance(value, str):
            raise ValueError("Categorical (string) value expected")

        self.attribute_value = value
        self.trigger = triggering_status
        self.probability = probability

    def execute(self, adjacency, edges, attributes, status_map, *args, **kwargs):
        '''
        adjacency is a non-symmetric adjacency matrix: if the edge i,j exists, in i,j there is the status of j, in j,i the status of i. otherwise, in i,j there is 0
        nb: statuses now start from 1
        nb: we assume that the graph is undirected
        '''
        # if isinstance(graph, nx.DiGraph):
        #     neighbors = list(graph.predecessors(node))
        # else:
        #     neighbors = list(graph.neighbors(node))

        if self.trigger is None:
            triggered = edges[self.attribute].get(self.attribute_value,csr_matrix(adjacency.shape))
        else:
            triggered = (adjacency==status_map[self.trigger]).multiply(edges[self.attribute].get(self.attribute_value,False))

        if triggered.count_nonzero():
            p = csr_matrix((np.random.random(triggered.count_nonzero()),triggered.nonzero()), shape=adjacency.shape)
            test = (p>=1-self.probability).sum(axis=1)
        else:
            test = np.zeros(adjacency.shape[0], dtype=bool)

        if np.any(test):
            return np.logical_and(test, self.compose(adjacency, edges, attributes, status_map, kwargs))
        else:
            return test
