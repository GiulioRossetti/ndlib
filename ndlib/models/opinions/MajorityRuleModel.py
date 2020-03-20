from ..DiffusionModel import DiffusionModel
import numpy as np

__author__ = "Alina Sirbu"
__email__ = "alina.sirbu@unipi.it"


class MajorityRuleModel(DiffusionModel):
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

        self.parameters = {"model": {
            "q": {
                "descr": "Number of randomly chosen voters",
                "range": [0, len(self.graph.nodes)],
                "optional": False
            }
        },
            "nodes": {},
            "edges": {}
        }

        self.name = "Majority Rule"

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """

        # One iteration changes the opinion of at most q voters using the following procedure:
        # - select randomly q voters
        # - compute majority opinion
        # - if tie all agents take opinion +1
        # - if not tie, all agents take majority opinion

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

        # select q random nodes
        discussion_group = [list(self.graph.nodes)[i]
                            for i in np.random.randint(0, self.graph.number_of_nodes(), self.params['model']['q'])]

        # compute majority
        majority_vote = 1
        vote_sum = sum([self.status[node] for node in discussion_group])
        if vote_sum < (self.params["model"]["q"] / 2.0):
            majority_vote = 0  # in case of tie, majority_vote remains 1

        # update status of nodes in discussion group
        delta = {}
        status_delta = {st: 0 for st in self.available_statuses.values()}

        for listener in discussion_group:
            if majority_vote != self.status[listener]:
                delta[listener] = majority_vote

                status_delta[self.status[listener]] += 1
                for x in self.available_statuses.values():
                    if x != self.status[listener]:
                        status_delta[x] -= 1

            self.status[listener] = majority_vote

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


