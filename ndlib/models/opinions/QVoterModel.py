from ..DiffusionModel import DiffusionModel
import networkx as nx
import numpy as np

__author__ = "Alina Sirbu"
__email__ = "alina.sirbu@unipi.it"


class QVoterModel(DiffusionModel):
    """
    Implements the q-voter model of opinion dynamics.
    Two model parameters:
    - the state of the initial population controlled by the proportion of
    "infected" individuals.
    - parameter "q" which controls the number of neighbours that affect the opinion of an agent

    """

    def __init__(self, graph):
        super(self.__class__, self).__init__(graph)
        self.available_statuses = {
            "Susceptible": 0,
            "Infected": 1
        }

        self.parameters = {"model": {
                "q": {
                    "descr": "Number of neighbours that affect the opinion of an agent",
                    "range": [0, len(self.graph.nodes())],
                    "optional": False
                }
            },
            "nodes": {},
            "edges": {}
        }

        self.name = "QVoter"

    def iteration(self):
        """
        One iteration changes the opinion of one voter using the following procedure:
        - select randomly one voter (listener)
        - select randomly q of its neighbours (speakers)
        - if the q neighbours agree, the listener takes their opinion
        """
        self.clean_initial_status(self.available_statuses.values())

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            return 0, self.status

        # select a random listener
        listener = self.graph.nodes()[np.random.randint(0, self.graph.number_of_nodes())]

        # select all of the listener's neighbours
        neighbours = self.graph.neighbors(listener)
        if isinstance(self.graph, nx.DiGraph):
            # consider only the predecessors
            # assumed if a->b then b can be influenced by a
            neighbours = self.graph.predecessors(listener)

        # select q random neighbours (with repetitions)
        influence_group_state = [self.status[neighbours[i]]
                                 for i in np.random.randint(0, len(neighbours), self.params['model']['q'])]

        delta = {}
        # if all neighbours agree (either on 0 or on 1)
        if sum(influence_group_state) == 0 or sum(influence_group_state) == len(influence_group_state):
            # update status of listener to either on of the neighbours selected
            delta[listener] = influence_group_state[0]
            self.status[listener] = influence_group_state[0]

        self.actual_iteration += 1

        return self.actual_iteration - 1, delta
