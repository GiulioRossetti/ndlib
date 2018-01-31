from ndlib.models.actions.Action import Action
import numpy as np

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class RemoveNode(Action):

    def __init__(self, probability=1, number_of_nodes=1, **kwargs):
        super(self.__class__, self).__init__(kwargs)
        self.probability = probability
        self.number_of_nodes = number_of_nodes

    def execute(self, graph=None, node=None, status=None, *args, **kwargs):

        p = np.random.random_sample()

        # Node creation check
        if p <= self.probability:

            if node is None:
                node = np.random.choice(list(graph.nodes()), self.number_of_nodes, replace=False)
            else:
                node = [node]

            for n in node:
                graph.remove_node(n)
                del status[n]

            return self.compose(graph, **kwargs)

        return True
