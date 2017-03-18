from ..DiffusionModel import DiffusionModel
import numpy as np

__author__ = "Alina Sirbu"
__email__ = "alina.sirbu@unipi.it"


class MajorityRuleModel(DiffusionModel):
    """
    Implements the majority rule model of opinion dynamics.
    One model parameter is the state of the initial population controlled by the proportion of
    "infected" individuals.
    Second model parameter is size of groups, "q". Better to have "q" odd.
    Applies to complete network setting (should not crash for other networks, but would not make sense).

    """

    def __init__(self, graph):
        super(self.__class__, self).__init__(graph)
        self.available_statuses = {
            "Susceptible": 0,
            "Infected": 1,
        }

        self.parameters = {"model": {
            "q": {
                "descr": "Number of randomly chosen voters",
                "range": [0, len(self.graph.nodes())],
                "optional": False
            }
        },
            "nodes": {},
            "edges": {}
        }

        self.name = "Majority Rule"

    def iteration(self):
        """
        One iteration changes the opinion of at most q voters using the following procedure:
        - select randomly q voters
        - compute majority opinion
        - if tie all agents take opinion +1
        - if not tie, all agents take majority opinion
        """
        self.clean_initial_status(self.available_statuses.values())

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            return self.actual_iteration, self.status

        # select q random nodes
        discussion_group = [self.graph.nodes()[i]
                            for i in np.random.randint(0, self.graph.number_of_nodes(), self.params['model']['q'])]

        # compute majority
        majority_vote = 1
        vote_sum = sum([self.status[node] for node in discussion_group])
        if vote_sum < (self.params["model"]["q"] / 2.0):
            majority_vote = 0  # in case of tie, majority_vote remains 1

        # update status of nodes in discussion group
        delta = {}
        for listener in discussion_group:
            if majority_vote != self.status[listener]:
                delta[listener] = majority_vote
            self.status[listener] = majority_vote

        self.actual_iteration += 1

        return self.actual_iteration - 1, delta
