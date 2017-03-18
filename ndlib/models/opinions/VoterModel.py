from ..DiffusionModel import DiffusionModel
import networkx as nx
import numpy as np

__author__ = "Alina Sirbu"
__email__ = "alina.sirbu@unipi.it"


class VoterModel(DiffusionModel):
    """
    Implements the voter model of opinion dynamics.
    The only model parameter is the state of the initial population controlled by the proportion of
    "infected" individuals

    """

    def __init__(self, graph):
        super(self.__class__, self).__init__(graph)
        self.available_statuses = {
            "Susceptible": 0,
            "Infected": 1
        }

        self.name = "Voter"

    def iteration(self):
        """
        One iteration changes the opinion of one voter using the following procedure:
        - select randomly one voter (listener)
        - selecting randomly one of its peers (speaker)
        - the first voter takes the opinion of the peer (listener takes the opinion of speaker)
        """

        self.clean_initial_status(self.available_statuses.values())

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            return 0, self.status

        # select a random node
        listener = self.graph.nodes()[np.random.randint(0, self.graph.number_of_nodes())]

        # select a random neighbour
        neighbours = self.graph.neighbors(listener)
        if isinstance(self.graph, nx.DiGraph):
            # difficult to have a digraph but assumed if a->b then b can be influenced by a
            # but not the other way around
            neighbours = self.graph.predecessors(listener)

        speaker = neighbours[np.random.randint(0, len(neighbours))]

        # update status of listener
        delta = {listener: self.status[speaker]}
        self.status[listener] = self.status[speaker]
        self.actual_iteration += 1

        return self.actual_iteration - 1, delta
