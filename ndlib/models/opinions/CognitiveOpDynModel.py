from ..DiffusionModel import DiffusionModel
import numpy as np
import future.utils

__author__ = "Alina Sirbu"
__email__ = "alina.sirbu@unipi.it"


class CognitiveOpDynModel(DiffusionModel):
    """
    Model Parameters to be specified via ModelConfig

    :param I: external information value in [0,1]
    :param T_range_min: the minimum of the range of initial values for  T. Range [0,1].
    :param T_range_max: the maximum of the range of initial values for  T. Range [0,1].
    :param B_range_min: the minimum of the range of initial values for  B. Range [0,1]
    :param B_range_max: the maximum of the range of initial values for  B. Range [0,1].
    :param R_fraction_negative: fraction of individuals having the node parameter R=-1.
    :param R_fraction_positive: fraction of individuals having the node parameter R=1
    :param R_fraction_neutral: fraction of individuals having the node parameter R=0

    The following relation should hold: R_fraction_negative+R_fraction_neutral+R_fraction_positive=1.
    To achieve this, the fractions selected will be normalised to sum 1.
    Node states are continuous values in [0,1].

    The initial state is generated randomly uniformly from the domain defined by model parameters.
    """

    def __init__(self, graph, seed=None):
        """
             Model Constructor

             :param graph: A networkx graph object
         """
        super(self.__class__, self).__init__(graph, seed)

        self.discrete_state = False

        self.available_statuses = {
            "Infected": 0
        }

        self.parameters = {
            "model": {
                "I": {
                    "descr": "External information",
                    "range": [0, 1],
                    "optional": False
                },
                "T_range_min": {
                    "descr": "Minimum of the range of initial values for T",
                    "range": [0, 1],
                    "optional": False
                },
                "T_range_max": {
                    "descr": "Maximum of the range of initial values for T",
                    "range": [0, 1],
                    "optional": False
                },
                "B_range_min": {
                    "descr": "Minimum of the range of initial values for B",
                    "range": [0, 1],
                    "optional": False
                },
                "B_range_max": {
                    "descr": "Maximum of the range of initial values for B",
                    "range": [0, 1],
                    "optional": False
                },
                "R_fraction_negative": {
                    "descr": "Fraction of nodes having R=-1",
                    "range": [0, 1],
                    "optional": False
                },
                "R_fraction_neutral": {
                    "descr": "Fraction of nodes having R=0",
                    "range": [0, 1],
                    "optional": False
                },
                "R_fraction_positive": {
                    "descr": "Fraction of nodes having R=1",
                    "range": [0, 1],
                    "optional": False
                }
            },
            "nodes": {},
            "edges": {}
        }

        self.name = "Cognitive Opinion Dynamics"

    def set_initial_status(self, configuration=None):
        """
        Override behaviour of methods in class DiffusionModel.
        Overwrites initial status using random real values.
        Generates random node profiles.
        """
        super(CognitiveOpDynModel, self).set_initial_status(configuration)

        # set node status
        for node in self.status:
            self.status[node] = np.random.random_sample()
        self.initial_status = self.status.copy()

        # set new node parameters
        self.params['nodes']['cognitive'] = {}

        # first correct the input model parameters and retreive T_range, B_range and R_distribution
        T_range = (self.params['model']['T_range_min'], self.params['model']['T_range_max'])
        if self.params['model']['T_range_min'] > self.params['model']['T_range_max']:
            T_range = (self.params['model']['T_range_max'], self.params['model']['T_range_min'])

        B_range = (self.params['model']['B_range_min'], self.params['model']['B_range_max'])
        if self.params['model']['B_range_min'] > self.params['model']['B_range_max']:
            B_range = (self.params['model']['B_range_max'], self.params['model']['B_range_min'])
        s = float(self.params['model']['R_fraction_negative'] + self.params['model']['R_fraction_neutral'] +
                  self.params['model']['R_fraction_positive'])
        R_distribution = (self.params['model']['R_fraction_negative']/s, self.params['model']['R_fraction_neutral']/s,
                          self.params['model']['R_fraction_positive']/s)

        # then sample parameters from the ranges and distribution
        for node in self.graph.nodes:
            R_prob = np.random.random_sample()
            if R_prob < R_distribution[0]:
                R = -1
            elif R_prob < (R_distribution[0] + R_distribution[1]):
                R = 0
            else:
                R = 1
            # R, B and T parameters in a tuple
            self.params['nodes']['cognitive'][node] = (R,
                                                       B_range[0] + (B_range[1] - B_range[0])*np.random.random_sample(),
                                                       T_range[0] + (T_range[1] - T_range[0])*np.random.random_sample())

    def clean_initial_status(self, valid_status=None):
        for n, s in future.utils.iteritems(self.status):
            if s > 1 or s < 0:
                self.status[n] = 0

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        # One iteration changes the opinion of all agents using the following procedure:
        # - first all agents communicate with institutional information I using a deffuant like rule
        # - then random pairs of agents are selected to interact  (N pairs)
        # - interaction depends on state of agents but also internal cognitive structure

        self.clean_initial_status(None)

        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(self.status)
            if node_status:
                return {"iteration": 0, "status": self.status.copy(),
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": 0, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}

        # first interact with I
        I = self.params['model']['I']
        for node in self.graph.nodes:
            T = self.params['nodes']['cognitive'][node][2]
            R = self.params['nodes']['cognitive'][node][0]
            actual_status[node] = actual_status[node] + T * (I - actual_status[node])
            if R == 1:
                actual_status[node] = 0.5 * (1 + actual_status[node])
            if R == -1:
                actual_status[node] *= 0.5

        # then interact with peers
        for i in range(0, self.graph.number_of_nodes()):
            # select a random node
            n1 = list(self.graph.nodes)[np.random.randint(0, self.graph.number_of_nodes())]

            # select all of the nodes neighbours (no digraph possible)
            neighbours = list(self.graph.neighbors(n1))
            if len(neighbours) == 0:
                continue

            # select second node - a random neighbour
            n2 = neighbours[np.random.randint(0, len(neighbours))]

            # update status of n1 and n2
            p1 = pow(actual_status[n1], 1.0 / self.params['nodes']['cognitive'][n1][1])
            p2 = pow(actual_status[n2], 1.0 / self.params['nodes']['cognitive'][n2][1])

            oldn1 = self.status[n1]
            if np.random.random_sample() < p2:  # if node 2 talks, node 1 gets changed
                T1 = self.params['nodes']['cognitive'][n1][2]
                R1 = self.params['nodes']['cognitive'][n1][0]
                actual_status[n1] += (1 - T1) * (actual_status[n2] - actual_status[n1])
                if R1 == 1:
                    actual_status[n1] = 0.5 * (1 + actual_status[n1])
                if R1 == -1:
                    actual_status[n1] *= 0.5
            if np.random.random_sample() < p1:  # if node 1 talks, node 2 gets changed
                T2 = self.params['nodes']['cognitive'][n2][2]
                R2 = self.params['nodes']['cognitive'][n2][0]
                actual_status[n2] += (1 - T2) * (oldn1 - actual_status[n2])
                if R2 == 1:
                    actual_status[n2] = 0.5 * (1 + actual_status[n2])
                if R2 == -1:
                    actual_status[n2] *= 0.5

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}

