from ..DiffusionModel import DiffusionModel
import networkx as nx
import numpy as np

__author__ = "Alina Sirbu"
__email__ = "alina.sirbu@unipi.it"


class SznajdModel(DiffusionModel):
    """
    Implements the Sznajd model of opinion dynamics.
    The only model parameter is the state of the initial population controlled by the proportion of
    "infected" individuals.

    """

    def __init__(self, graph):
        super(self.__class__, self).__init__(graph)
        self.available_statuses = {
            "Susceptible": 0,
            "Infected": 1,
         }

        self.name = "Sznajd"

    def iteration(self):
        """
        One iteration changes the opinion of several voters using the following procedure:
        - select randomly one voter (speaker 1)
        - select randomly one of its neighbours (speaker 2)
        - if the two voters agree, their neighbours take their opinion
        """

        self.clean_initial_status(self.available_statuses.values())

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            return 0, self.status
        delta = {}
        # select a random node
        speaker1 = self.graph.nodes()[np.random.randint(0, self.graph.number_of_nodes())]

        # select a random neighbour
        neighbours = self.graph.neighbors(speaker1)
        if isinstance(self.graph, nx.DiGraph):
            # add also the predecessors
            neighbours += self.graph.predecessors(speaker1)

        speaker2 = neighbours[np.random.randint(0, len(neighbours))]

        if self.status[speaker1] == self.status[speaker2]:
            # select listeners (all neighbours of two speakers)
            neighbours = self.graph.neighbors(speaker1) + self.graph.neighbors(speaker2)

            if isinstance(self.graph, nx.DiGraph):
                # assumed if a->b then b can be influenced by a
                # but not the other way around - the link between the speakers doesn't matter
                neighbours = self.graph.successors(speaker1) + self.graph.successors(speaker2)

            # update status of listeners
            for listener in neighbours:
                if self.status[speaker1] != self.status[listener]:
                    delta[listener] = self.status[speaker1]
                self.status[listener] = self.status[speaker1]

        self.actual_iteration += 1

        return self.actual_iteration - 1, delta
