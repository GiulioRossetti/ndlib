from ndlib.models.DiffusionModel import DiffusionModel
import future.utils
import numpy as np
import random
from sklearn.metrics import jaccard_score

__author__ = 'Cecilia Toccaceli'
__license__ = "BSD-2-Clause"

class WHKModel(DiffusionModel):
    """
    Model Parameters to be specified via ModelConfig
    :param epsilon: bounded confidence threshold from the HK model (float in [0,1])
    :param perc_stubborness: Percentage of stubborn agent (float in [0,1], default 0)
    :param option_for_stubbornness: Define distribution of stubborns (in {-1,0,1}, default 0)
    :param similarity: the method uses the similarity or not  ( in {0,1}, default 0)
    :param weight: the weight of edges (float in [0,1])
    :param stubborn: The agent is stubborn or not ( in {0,1}, default 0)
    :param vector: represents the character of the node (list in [0,1], default [])
    """

    def __init__(self, graph):
        """
        Model Constructor
        :param graph: A networkx graph object
        """
        super(self.__class__, self).__init__(graph)
        self.discrete_state = False

        self.available_statuses = {
            "Infected": 0
        }

        self.parameters = {
            "model": {
                "epsilon": {
                    "descr": "Bounded confidence threshold",
                    "range": [0, 1],
                    "optional": False,
                },
                "perc_stubborness": {
                    "descr": "Percentage of stubborn agent",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
                "option_for_stubbornness": {
                    "descr": "Define distribution of stubborns",
                    "range": {-1, 0, 1},
                    "optional": True,
                    "default": 0
                },
                "similarity": {
                    "descr": "The method use the feature of the nodes ot not",
                    "range": {0, 1},
                    "optional": True,
                    "default": 0
                }
            },
            "edges": {
                "weight": {
                    "descr": "Edge weight",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.1
                }
            },
            "nodes": {
                "stubborn": {
                    "descr": "The agent is stubborn or not",
                    "range": {0, 1},
                    "optional": True,
                    "default": 0
                },
                "vector": {
                    "descr": "Vector represents the character of the node",
                    "range": float,
                    "optional": True,
                    "default": []
                }
            },
        }
        self.name = "Weight HK"

    def set_initial_status(self, configuration=None):
        """
        Override behaviour of methods in class DiffusionModel.
        Overwrites initial status using random real values.
        """
        super(WHKModel, self).set_initial_status(configuration)

        # set node status
        for node in self.status:
            self.status[node] = random.uniform(-1, 1)
        self.initial_status = self.status.copy()

    '''
    For each node n, check the status s
    if s isn't included between -1 and 1 excluded, set s to 0.0
    '''

    def clean_initial_status(self, valid_status=None):
        for n, s in future.utils.iteritems(self.status):
            if s > 1 or s < -1:
                self.status[n] = 0.0

    def iteration(self, node_status=True):

        '''
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary code -> status)
        '''
        # An iteration changes the opinion of the selected agent 'i' using the following procedure:
        # if i is stubborn then its status doesn't change, else
        # - select all its neighbors
        # - if between each pair of agents, there is a smaller distance than epsilon, then
        # the state of the agent change, becoming the sum between its initial opinion and
        # the average of weighted opinions of its neighbors
        # multiplied by a different factor based on the sign of the agent's (i) opinion.

        self.clean_initial_status(None)

        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        if self.actual_iteration == 0:
            use_stubborn_node = False
            negatives = []
            positives = []
            for node in self.graph.nodes:
                if self.params['model']['similarity'] == 1:
                    # use the similarity vector
                    # create binary vector for the agent character
                    i = 0
                    if len(self.params['nodes']['vector'][node]) == 0:
                    #self.params['nodes']['vector'][node] = []
                        while i < 5:
                            self.params['nodes']['vector'][node].append(np.random.randint(2))
                            i += 1
                if self.params['nodes']['stubborn'][node] == 1:
                    # use the stubborn nodes
                    use_stubborn_node = True
                # if stubborns have intermediate negative opinions
                '''if actual_status[node]>=-0.6 and actual_status[node]<=-0.4:'''
                if actual_status[node] <= -0.8:
                    if node not in negatives:
                        negatives.append(node)
                # if stubborns have intermediate positive opinions
                '''if actual_status[node] >= 0.4 and actual_status[node]<=0.6:'''
                if actual_status[node] >= 0.8:
                    if node not in positives:
                        positives.append(node)

            join_list = negatives + positives
            num_stubborns = 0
            if use_stubborn_node == False:
                # based on the value of option_for_stubbornness, compute num_stubborns or only on negatives, or on positives or on the union of the two
                if self.params['model']['option_for_stubbornness'] == -1 and len(negatives) != 0:
                    num_stubborns = int(float(len(negatives)) * float(self.params['model']['perc_stubborness']))
                elif self.params['model']['option_for_stubbornness'] == 1 and len(positives) != 0:
                    num_stubborns = int(float(len(positives)) * float(self.params['model']['perc_stubborness']))
                elif self.params['model']['option_for_stubbornness'] == 0 and len(join_list) != 0:
                    num_stubborns = int(float(len(join_list)) * float(self.params['model']['perc_stubborness']))

                count_stub = 0

                while count_stub < num_stubborns:
                    if self.params['model']['option_for_stubbornness'] == -1:
                        n = random.choice(negatives)
                    elif self.params['model']['option_for_stubbornness'] == 1:
                        n = random.choice(positives)
                    elif self.params['model']['option_for_stubbornness'] == 0:
                        n = random.choice(join_list)

                    if self.params['nodes']['stubborn'][n] == 0:
                        self.params['nodes']['stubborn'][n] = 1
                        count_stub += 1

                # if num_stubborns is compute with uniform distribution over the entire population (option_for_stubbornness is not used in this case)
                '''
                num_stubborns = 0
                if setting == False:
                    num_stubborns = int(float(self.graph.number_of_nodes())*float(self.params['model']['perc_stubborness']))
                    count_stub = 0

                    while count_stub < num_stubborns:
                        n = list(self.graph.nodes)[np.random.randint(0,self.graph.number_of_nodes())]
                        if self.params['nodes']['stubborn'][n] == 0:
                            self.params['nodes']['stubborn'][n] = 1
                            count_stub += 1
                '''

            self.actual_iteration += 1
            # delta, node_count, status_delta = self.status_delta(self.status)
            if node_status:
                return {"iteration": 0, "status": self.status.copy(),
                        "node_count": len(self.status), "status_delta": self.status.copy()}
            else:
                return {"iteration": 0, "status": {},
                        "node_count": len(self.status), "status_delta": self.status.copy()}

        '''
        - select a random agent n1
        - if it is stubborn:
            its status doesn't change 
        - else:
            - select all its neighbors
            - for each neighbor, diff_opinion is compute
            - if diff_opinion < epsilon then:
                sum the weighted opinion of the neighbor to the sum_op
            - compute new_op (updated opinion of n1)
        '''
        for i in range(0, self.graph.number_of_nodes()):
            # select a random node
            n1 = list(self.graph.nodes)[np.random.randint(0, self.graph.number_of_nodes())]

            # if n1 isn't stubborn
            if self.params['nodes']['stubborn'][n1] == 0:
                # select neighbors of n1
                neighbours = list(self.graph.neighbors(n1))
                sum_op = 0
                count_in_eps = 0

                if len(neighbours) == 0:
                    continue

                for neigh in neighbours:
                    key = (n1, neigh)

                    # compute the difference between opinions
                    diff_opinion = np.abs((actual_status[n1]) - (actual_status[neigh]))
                    if diff_opinion < self.params['model']['epsilon']:
                        jaccard_sim = 0
                        if self.params['model']['similarity'] == 1:
                            # compute similarity between n1 and neigh using jaccard score
                            jaccard_sim = jaccard_score(self.params['nodes']['vector'][n1],
                                                        self.params['nodes']['vector'][neigh])
                        weight = 0
                        if not self.graph.has_edge(key[0], key[1]):
                            e = list(key)
                            reverse = [e[1], e[0]]
                            link = tuple(reverse)
                            if link in self.params['edges']['weight']:
                                weight = (self.params['edges']['weight'][link])
                            elif not self.graph.directed:
                                weight = (self.params['edges']['weight'][key])
                        else:
                            if key in self.params['edges']['weight']:
                                weight = (self.params['edges']['weight'][key])
                            elif not self.graph.directed:
                                weight = (self.params['edges']['weight'][(key[1], key[0])])

                        if self.params['model']['similarity'] == 1:
                            sum_op += (actual_status[neigh] * weight) * jaccard_sim
                        else:
                            sum_op += (actual_status[neigh] * weight)
                        # count_in_eps is the number of neighbors in epsilon
                        count_in_eps += 1

                if (count_in_eps > 0):
                    if actual_status[n1] > 0:
                        new_op = actual_status[n1] + ((sum_op / count_in_eps) * (1 - actual_status[n1]))
                    elif actual_status[n1] <= 0:
                        new_op = actual_status[n1] + ((sum_op / count_in_eps) * (1 + actual_status[n1]))

                else:
                    # if there aren't neighbors in epsilon, the status of n1 doesn't change
                    new_op = actual_status[n1]
            # if n1 is stubborn
            else:
                # opinion doesn't change
                new_op = actual_status[n1]

            actual_status[n1] = new_op

        # delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1
        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": self.status.copy(), "node_count": len(actual_status),
                    "status_delta": self.status.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {}, "node_count": len(actual_status),
                    "status_delta": self.status.copy()}
