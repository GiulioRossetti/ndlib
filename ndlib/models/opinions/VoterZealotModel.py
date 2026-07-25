from ..DiffusionModel import DiffusionModel
import numpy as np

__author__ = "Antigravity"
__license__ = "BSD-2-Clause"


class VoterZealotModel(DiffusionModel):
    """
    Model Constructor
    :param graph: A networkx graph object
    """

    def __init__(self, graph, seed=None):
        super(self.__class__, self).__init__(graph, seed)
        self.available_statuses = {"Susceptible": 0, "Infected": 1}

        self.parameters = {
            "model": {},
            "edges": {},
            "nodes": {
                "zealot": {
                    "descr": "Whether the node is a zealot (immutable opinion)",
                    "range": {0, 1},
                    "optional": True,
                    "default": 0,
                }
            },
        }
        self.name = "Voter with Zealots"

    def iteration(self, node_status=True):
        """
        Execute a single model iteration
        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        self.clean_initial_status(self.available_statuses.values())

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(self.status)
            if node_status:
                return {
                    "iteration": 0,
                    "status": self.status.copy(),
                    "node_count": node_count.copy(),
                    "status_delta": status_delta.copy(),
                }
            else:
                return {
                    "iteration": 0,
                    "status": {},
                    "node_count": node_count.copy(),
                    "status_delta": status_delta.copy(),
                }

        # select a random node
        listener = list(self.graph.nodes)[
            np.random.randint(0, self.graph.number_of_nodes())
        ]

        delta = {}
        status_delta = {st: 0 for st in self.available_statuses.values()}

        is_zealot = 0
        if "zealot" in self.params["nodes"] and listener in self.params["nodes"]["zealot"]:
            is_zealot = self.params["nodes"]["zealot"][listener]

        if is_zealot == 0:
            # select a random neighbour
            neighbours = list(self.graph.neighbors(listener))
            if self.graph.directed:
                neighbours = list(self.graph.predecessors(listener))

            if len(neighbours) > 0:
                speaker = neighbours[np.random.randint(0, len(neighbours))]
                speaker_opinion = self.status[speaker]
                old_opinion = self.status[listener]

                if old_opinion != speaker_opinion:
                    delta = {listener: speaker_opinion}
                    self.status[listener] = speaker_opinion
                    status_delta[speaker_opinion] += 1
                    status_delta[old_opinion] -= 1

        node_count = {
            st: len([n for n in self.status if self.status[n] == st])
            for st in self.available_statuses.values()
        }

        self.actual_iteration += 1

        if node_status:
            return {
                "iteration": self.actual_iteration - 1,
                "status": delta.copy(),
                "node_count": node_count.copy(),
                "status_delta": status_delta.copy(),
            }
        else:
            return {
                "iteration": self.actual_iteration - 1,
                "status": {},
                "node_count": node_count.copy(),
                "status_delta": status_delta.copy(),
            }
