from ndlib.models.actions.Action import Action
import numpy as np
import networkx as nx

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class RemoveNode(Action):

    def __init__(self, probability=1, number_of_nodes=1, model='random', **kwargs):
        super(self.__class__, self).__init__(kwargs)
        self.probability = probability
        self.number_of_nodes = number_of_nodes
        self.model =  model

    def execute(self, graph=None, node=None, status=None, *args, **kwargs):

        p = np.random.random_sample()

        # Node creation check
        if p <= self.probability:

            if node is None:

                total_edges = graph.number_of_edges()
                if isinstance(graph, nx.Graph):
                    total_edges *= 2

                if self.model == 'top':
                    probs = [float(graph.degree(n)) / total_edges for n in graph.nodes()]
                elif self.model == 'bottom':
                    probs = [1 - (float(graph.degree(n)) / total_edges) for n in graph.nodes()]
                    tot = sum(probs)
                    probs = [float(x)/tot for x in probs]
                else:
                    probs = None

                node = np.random.choice(list(graph.nodes()), self.number_of_nodes, replace=False, p=probs)
            else:
                node = [node]

            for n in node:
                graph.remove_node(n)
                del status[n]

            return self.compose(graph, **kwargs)

        return True
