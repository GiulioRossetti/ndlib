from ..DiffusionModel import DiffusionModel
import numpy as np

__author__ = "Alina Sirbu"
__email__ = "alina.sirbu@unipi.it"


class QVoterModel(DiffusionModel):
    """
    Node Parameters to be specified via ModelConfig

    :param q: the number of neighbors that affect the opinion of a node
    """

    def __init__(self, graph, seed=None):
        """
             Model Constructor

             :param graph: A networkx graph object
         """
        super(self.__class__, self).__init__(graph, seed)
        self.available_statuses = {
            "Susceptible": 0,
            "Infected": 1
        }

        self.parameters = {"model": {
                "q": {
                    "descr": "Number of neighbours that affect the opinion of an agent",
                    "range": [0, len(self.graph.nodes)],
                    "optional": False
                }
            },
            "nodes": {},
            "edges": {}
        }

        self.name = "QVoter"

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        # One iteration changes the opinion of one voter using the following procedure:
        # - select randomly one voter (listener)
        # - select randomly q of its neighbours (speakers)
        # - if the q neighbours agree, the listener takes their opinion

        self.clean_initial_status(self.available_statuses.values())

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(self.status)
            if node_status:
                return {"iteration": 0, "status": self.status.copy(),
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": 0, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}

                # select a random listener
        listener = list(self.graph.nodes)[np.random.randint(0, self.graph.number_of_nodes())]

        # select all of the listener's neighbours
        neighbours = list(self.graph.neighbors(listener))
        if self.graph.directed:
            # consider only the predecessors
            # assumed if a->b then b can be influenced by a
            neighbours = list(self.graph.predecessors(listener))

        # select q random neighbours (with repetitions)
        influence_group_state = [self.status[neighbours[i]]
                                 for i in np.random.randint(0, len(neighbours), self.params['model']['q'])]

        delta = {}
        # if all neighbours agree (either on 0 or on 1)
        status_delta = {st: 0 for st in self.available_statuses.values()}

        if sum(influence_group_state) == 0 or sum(influence_group_state) == len(influence_group_state):
            # update status of listener to either on of the neighbours selected
            delta[listener] = influence_group_state[0]
            self.status[listener] = influence_group_state[0]
            status_delta[self.status[listener]] += 1
            for x in self.available_statuses.values():
                if x != self.status[listener]:
                    status_delta[x] -= 1
        # fix
        node_count = {st: len([n for n in self.status if self.status[n] == st])
                      for st in self.available_statuses.values()}

        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}

