from ndlib.models.actions.Action import Action
import numpy as np
import networkx as nx

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class AddNode(Action):

    def __init__(self, probability=1, copy_attributes=False, initial_status=None, **kwargs):
        super(self.__class__, self).__init__(kwargs)
        self.probability = probability
        self.copy_attributes = copy_attributes
        self.initial_status = initial_status

    def execute(self, graph=None, status=None, status_map=None, *args, **kwargs):

        p = np.random.random_sample()

        # Node creation check
        if p <= self.probability:
            attr = None
            if self.copy_attributes:
                # randomly select a graph node
                ncd = np.random.choice(list(graph.nodes()))
                # create a copy of the node attribute
                attr = graph.nodes[ncd]

            nid = graph.number_of_nodes()+1
            graph.add_node(nid, attr=attr)
            for key in attr.keys():
                nx.set_node_attributes(graph, name=key, values={nid: key})

            status[nid] = status_map[self.initial_status]
            return self.compose(graph, node_id=nid, **kwargs)

        return True
