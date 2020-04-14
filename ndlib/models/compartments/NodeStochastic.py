from ndlib.models.compartments.Compartment import Compartiment
import numpy as np

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
        try:
            directed = graph.directed
        except AttributeError:
            directed = graph.is_directed()

        if directed:
            neighbors = graph.predecessors(node)

        p = np.random.random_sample()
        if self.trigger is None:
            triggered = 1
        else:
            triggered = 1 if len([v for v in neighbors if status[v] == status_map[self.trigger]]) > 0 else 0

        test = p < self.rate * triggered
        if test:
            return self.compose(node, graph, status, status_map, kwargs)

        return False


## STEFANO: NEW ARRAY BASED COMPARTMENT
class NodeStochasticArray(Compartiment):

    def __init__(self, rate, triggering_status=None, **kwargs):
        super(self.__class__, self).__init__(kwargs)
        self.rate = rate
        self.trigger = triggering_status

    def execute(self, adjacency, edges, attributes, status_map, *args, **kwargs):
        '''
        adjacency is a non-symmetric adjacency matrix: if the edge i,j exists, in i,j there is the status of j, in j,i the status of i. otherwise, in i,j there is 0
        nb: statuses now start from 1
        nb: we assume that the graph is undirected
        '''
        # try:
        #     directed = graph.directed
        # except AttributeError:
        #     directed = graph.is_directed()
        #
        # if directed:
        #     neighbors = graph.predecessors(node)
        # else:
        #     neighbors = graph.neighbors(node)
        
        p = np.random.random(adjacency.shape[0])
        if self.trigger is None:
            triggered = np.ones(adjacency.shape[0], dtype=bool)
        else:
            triggered = (adjacency==status_map[self.trigger]).sum(axis=1)
            
        test = (p < (self.rate*triggered))
        if np.any(test):
            return np.logical_and(test, self.compose(adjacency, edges, attributes, status_map, kwargs))
        else:
            return test
