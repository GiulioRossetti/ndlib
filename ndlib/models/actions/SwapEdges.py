from ndlib.models.actions.Action import Action
import numpy as np
import networkx as nx

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class SwapEdges(Action):

    def __init__(self, probability=1, copy_attributes=False, number_of_swaps=1, **kwargs):
        super(self.__class__, self).__init__(kwargs)
        self.probability = probability
        self.copy_attributes = copy_attributes
        self.number_of_swaps = number_of_swaps

    def execute(self, graph=None, *args, **kwargs):

        p = np.random.random_sample()

        if p <= self.probability:
            attrs = None
            e1, e2 = None, None
            for it in range(0, self.number_of_swaps):
                # randomly select tw graph edges
                edges = list(graph.edges())
                eids = list(np.random.choice(range(0, len(edges)), 2, replace=False))

                e1, e2 = edges[eids[0]], edges[eids[1]]

                if self.copy_attributes:
                    # create a copy of the node attribute
                    attrs = [graph.edges[e1[0], e1[1]], graph.edges[e2[0], e2[1]]]

            x, y = e1[0], e1[1]
            u, v = e2[0], e2[1]
            graph.remove_edge(x, y)
            graph.remove_edge(u, v)

            if self.copy_attributes:
                graph.add_edge(x, v)
                graph.add_edge(y, u)
                for key in attrs[0].keys():
                    nx.set_edge_attributes(graph, name=key, values={(x, v): attrs[0][key], (u, y): attrs[1][key]})

            else:
                graph.add_edge(x, v, attrs)
                graph.add_edge(y, u, attrs)

            return self.compose(graph, **kwargs)

        return True
