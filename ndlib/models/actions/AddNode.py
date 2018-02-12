from ndlib.models.actions.Action import Action
import numpy as np
import networkx as nx

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class AddNode(Action):

    def __init__(self, probability=1, copy_attributes=False, number_of_edges=0, model='random',
                 initial_status=None, **kwargs):
        super(self.__class__, self).__init__(kwargs)
        self.probability = probability
        self.copy_attributes = copy_attributes
        self.initial_status = initial_status
        self.number_of_edges = number_of_edges
        self.model = model

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

            # Edge creation phase
            if self.number_of_edges > 0:
                # Preferential Attachment
                if self.model == 'PA':
                    total_edges = graph.number_of_edges()
                    if isinstance(graph, nx.Graph):
                        total_edges *= 2
                    probs = [float(graph.degree(n))/total_edges for n in graph.nodes()]
                # Random selection
                else:
                    probs = None

                if self.number_of_edges > graph.number_of_nodes():
                    self.number_of_edges = graph.number_of_nodes()

                targets = np.random.choice(list(graph.nodes()), self.number_of_edges, replace=False, p=probs)
                for tr in targets:
                    graph.add_edge(nid, tr)

            return self.compose(graph, node_id=nid, **kwargs)

        return True
