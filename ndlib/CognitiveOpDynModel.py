from DiffusionModel import DiffusionModel
import numpy as np

__author__ = "Alina Sirbu"
__email__ = "alina.sirbu@unipi.it"


class CognitiveOpDynModel(DiffusionModel):
    """
    Implements the cognitive model of opinion dynamics by Villone et al.
    One model parameter: 'I' external information value in [0,1].
    Node states are continuous values in [0,1].
    Additional node parameters encode risk sensitivity R in {0,-1,+1}, tendency to communicate B in [0,1], trust towards institutions T in [0,1].  These are stored in the 'cognitive' node parameter.
    The initial state is generated randomly uniformly from the domain.
    """

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
        RDomain = [-1, 0, 1]
        self.params['nodes']['cognitive'] = {}
        for node in self.graph.nodes():
            # R, B and T parameters in a tuple
            self.params['nodes']['cognitive'][node] = (
            RDomain[np.random.randint(0, 3)], np.random.random_sample(), np.random.random_sample())

    def iteration(self):
        """
        One iteration changes the opinion of all agents using the following procedure:
        - first all agents communicate with institutional information I using a deffuant like rule
        - then random pairs of agents are selected to interact  (N pairs)
        - interaction depends on state of agents but also internal cognitive structure
        """

        # first interact with I
        I = self.params['I']
        for node in self.graph.nodes():
            T = self.params['nodes']['cognitive'][node][2]
            R = self.params['nodes']['cognitive'][node][0]
            self.status[node] = self.status[node] + T * (I - self.status[node])
            if R == 1:
                self.status[node] = 0.5 * (1 + self.status[node])
            if R == -1:
                self.status[node] *= 0.5

        # then interact with peers
        for i in range(0, self.graph.number_of_nodes()):
            # select a random node
            n1 = self.graph.nodes()[np.random.randint(0, self.graph.number_of_nodes())]

            # select all of the nodes neighbours (no digraph possible)
            neighbours = self.graph.neighbors(n1)

            # select second node - a random neighbour
            n2 = neighbours[np.random.randint(0, len(neighbours))]

            # update status of n1 and n2
            p1 = pow(self.status[n1], 1.0 / self.params['nodes']['cognitive'][n1][1])
            p2 = pow(self.status[n2], 1.0 / self.params['nodes']['cognitive'][n2][1])

            oldn1 = self.status[n1]
            if np.random.random_sample() < p2:  # if node 2 talks, node 1 gets changed
                T1 = self.params['nodes']['cognitive'][n1][2]
                R1 = self.params['nodes']['cognitive'][n1][0]
                self.status[n1] += (1 - T1) * (self.status[n2] - self.status[n1])
                if R1 == 1:
                    self.status[n1] = 0.5 * (1 + self.status[n1])
                if R1 == -1:
                    self.status[n1] *= 0.5

            if np.random.random_sample() < p1:  # if node 1 talks, node 2 gets changed
                T2 = self.params['nodes']['cognitive'][n2][2]
                R2 = self.params['nodes']['cognitive'][n2][0]
                self.status[n2] += (1 - T2) * (oldn1 - self.status[n2])
                if R2 == 1:
                    self.status[n2] = 0.5 * (1 + self.status[n2])
                if R2 == -1:
                    self.status[n2] *= 0.5

        self.actual_iteration += 1

        return self.actual_iteration, self.status
