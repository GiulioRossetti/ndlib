from DiffusionModel import DiffusionModel
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

    def iteration(self):
        """
        One iteration changes the opinion of at most q voters using the following procedure:
        - select randomly q voters
        - compute majority opinion
        - if tie all agents take opinion +1
        - if not tie, all agents take majority opinion
        """
        self.clean_initial_status([0, 1])

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            return self.actual_iteration, self.status

        # select q random nodes
        discussion_group = [self.graph.nodes()[i]
                            for i in np.random.randint(0, self.graph.number_of_nodes(), self.params['q'])]

        # compute majority
        majority_vote = 1
        vote_sum = sum([self.status[node] for node in discussion_group])
        if vote_sum < (self.params["q"] / 2.0):
            majority_vote = 0  # in case of tie, majority_vote remains 1

        # update status of nodes in discussion group
        delta = {}
        for listener in discussion_group:
            delta[listener] = majority_vote
            self.status[listener] = majority_vote

        self.actual_iteration += 1

        return self.actual_iteration - 1, delta
