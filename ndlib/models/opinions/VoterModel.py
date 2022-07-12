from ..DiffusionModel import DiffusionModel
import numpy as np

__author__ = "Alina Sirbu"
__email__ = "alina.sirbu@unipi.it"


class VoterModel(DiffusionModel):
    """

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

        self.name = "Voter"

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        # One iteration changes the opinion of one voter using the following procedure:
        # - select randomly one voter (listener)
        # - selecting randomly one of its peers (speaker)
        # - the first voter takes the opinion of the peer (listener takes the opinion of speaker)

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

        # select a random node
        listener = list(self.graph.nodes)[np.random.randint(0, self.graph.number_of_nodes())]

        # select a random neighbour
        neighbours = list(self.graph.neighbors(listener))
        if self.graph.directed:
            # difficult to have a digraph but assumed if a->b then b can be influenced by a
            # but not the other way around
            neighbours = list(self.graph.predecessors(listener))

        speaker = neighbours[np.random.randint(0, len(neighbours))]

        # update status of listener
        delta = {listener: self.status[speaker]}
        self.status[listener] = self.status[speaker]

        # fix
        node_count = {st: len([n for n in self.status if self.status[n] == st])
                      for st in self.available_statuses.values()}
        status_delta = {st: 0 for st in self.available_statuses.values()}
        status_delta[self.status[speaker]] += 1
        for x in self.available_statuses.values():
            if x != self.status[speaker]:
                status_delta[x] -= 1

        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}

