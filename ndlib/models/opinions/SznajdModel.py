from ..DiffusionModel import DiffusionModel
import numpy as np

__author__ = "Alina Sirbu"
__email__ = "alina.sirbu@unipi.it"


class SznajdModel(DiffusionModel):
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
            "Infected": 1,
         }

        self.name = "Sznajd"

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        # One iteration changes the opinion of several voters using the following procedure:
        # - select randomly one voter (speaker 1)
        # - select randomly one of its neighbours (speaker 2)
        # - if the two voters agree, their neighbours take their opinion

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

        delta = {}
        status_delta = {st: 0 for st in self.available_statuses.values()}

        # select a random node
        speaker1 = list(self.graph.nodes)[np.random.randint(0, self.graph.number_of_nodes())]

        # select a random neighbour
        neighbours = list(self.graph.neighbors(speaker1))
        if self.graph.directed:
            # add also the predecessors
            neighbours += list(self.graph.predecessors(speaker1))

        speaker2 = neighbours[np.random.randint(0, len(neighbours))]

        if self.status[speaker1] == self.status[speaker2]:
            # select listeners (all neighbours of two speakers)
            neighbours = list(self.graph.neighbors(speaker1)) + list(self.graph.neighbors(speaker2))

            if self.graph.directed:
                # assumed if a->b then b can be influenced by a
                # but not the other way around - the link between the speakers doesn't matter
                neighbours = list(self.graph.successors(speaker1)) + list(self.graph.successors(speaker2))

            # update status of listeners
            for listener in neighbours:
                if self.status[speaker1] != self.status[listener]:
                    delta[listener] = self.status[speaker1]
                    status_delta[self.status[listener]] += 1
                    for x in self.available_statuses.values():
                        if x != self.status[listener]:
                            status_delta[x] -= 1

                self.status[listener] = self.status[speaker1]

        node_count = {st: len([n for n in self.status if self.status[n] == st])
                      for st in self.available_statuses.values()}

        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}


