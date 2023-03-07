from ndlib.models.DiffusionModel import DiffusionModel
import numpy as np
from random import choice
import future.utils
from collections import defaultdict
import tqdm
import random

__author__ = ["Alina Sirbu", "Giulio Rossetti", "Valentina Pansanella"]
__email__ = ["alina.sirbu@unipi.it", "giulio.rossetti@isti.cnr.it", "valentina.pansanella@sns.it"]


class AdaptivePeerPressureAlgorithmicBiasModel(DiffusionModel):
    """
    Model Parameters to be specified via ModelConfig

    :param epsilon: bounded confidence threshold from the Deffuant model, in [0,1]
    :param gamma: strength of the algorithmic bias, positive, real

    Node states are continuous values in [0,1].

    The initial state is generated randomly uniformly from the domain [0,1].
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
                "epsilon": {
                    "descr": "Bounded confidence threshold",
                    "range": [0, 1],
                    "optional": False
                },
                "gamma": {
                    "descr": "Algorithmic bias",
                    "range": [0, 100],
                    "optional": False
                },
                "p":{
                    "descr":"Rewiring probability",
                    "range":[0,1],
                    "optional": False
                }
            },
            "nodes": {},
            "edges": {}
        }

        self.name = "Adaptive Agorithmic Bias"

        self.node_data = {}
        self.ids = None
        self.sts = None

    def set_initial_status(self, configuration=None, opinions = 'default'):

        """
        Override behaviour of methods in class DiffusionModel.
        Overwrites initial status using random real values.
        """
        super(AdaptivePeerPressureAlgorithmicBiasModel, self).set_initial_status(configuration)

        for node in self.status:
            if opinions == 'default':
                self.status[node] = np.random.random_sample()
            else:
                self.status[node] = opinions[node]
        self.initial_status = self.status.copy()

        ### Initialization numpy representation

        max_edgees = (self.graph.number_of_nodes() * (self.graph.number_of_nodes() - 1)) / 2
        nids = np.array(list(self.status.items()))
        self.ids = nids[:, 0]

        if max_edgees == self.graph.number_of_edges(): #se la rete è completa
            self.sts = nids[:, 1]

        else: #se la rete non è completa
            for i in self.graph.nodes:
                i_neigh = list(self.graph.neighbors(i))
                i_ids = nids[:, 0][i_neigh]
                i_sts = nids[:, 1][i_neigh]

                self.node_data[i] = (i_ids, i_sts)

    @staticmethod
    def prob(distance, gamma, min_dist):
        if distance < min_dist:
            distance = min_dist
        return np.power(distance, -gamma)

    def pb1(self, statuses, i_status):
        dist = np.abs(statuses - i_status)
        null = np.full(statuses.shape[0], 0.00001)
        max_base = np.maximum(dist, null)
        dists = max_base ** -self.params['model']['gamma']
        return dists
    
    def rewiring(self, nodes, actual_status, n1, n2, eps):
        nodes_to_choose = nodes-set(self.graph.neighbors(n1))
        nodes_to_choose = list(nodes_to_choose)
        n3 = int(choice(nodes_to_choose))        
        if np.abs(actual_status[n1]-actual_status[n3]) < eps:
            self.graph.remove_edges(n1, [n2])
            self.graph.add_edges(n1, [n3])
            diff = 0.00001 #così non viene contata nelle steady iterations anche se effettivamente l'opinione non cambia
        else:
            diff = -1
        return diff

    def select_triangle(self, actual_status, n1, n2, neigh_ids, gam):
        neigh_n1 = neigh_ids
        neigh_n2 = self.graph.neighbors(n2)
        common = set(neigh_n1).intersection(neigh_n2)
        if len(common)>0:
            neigh_sts = np.array([actual_status[id] for id in common])
            selection_prob = self.pb1(neigh_sts, actual_status[n1])
            total = np.sum(selection_prob)
            selection_prob = selection_prob / total
            cumulative_selection_probability = np.cumsum(selection_prob)
            r = np.random.random_sample()
            n3 = np.argmax(
                cumulative_selection_probability >= r)
            n3 = int(neigh_ids[n3])
            return n3
        else:
            #nothing changes here. we go to the other rule
            return -1


    def peerpressure(self, nodes, actual_status, u, v, z, eps):
        if abs(actual_status[u]-actual_status[v])<eps:
            nn = (actual_status[u]+actual_status[v]) / 2.0
            if abs(actual_status[z]-nn) < eps:
                nnn = (actual_status[u]+actual_status[v]+actual_status[z]) / 3.0
                diff = max(abs(nnn-actual_status[u]), abs(nnn-actual_status[v]), abs(nnn-actual_status[z]))
                actual_status[u]=actual_status[v]=actual_status[z]=nnn
            else:
                diff = max(abs(nn-actual_status[u]), abs(nn-actual_status[v]), abs(nn-actual_status[z]))
                actual_status[u]=actual_status[v]=actual_status[z]=nn
        elif abs(actual_status[u]-actual_status[z])<eps:
            nn = (actual_status[u]+actual_status[z]) / 2.0
            if abs(actual_status[v]-nn) < eps:
                nnn = (actual_status[u]+actual_status[v]+actual_status[z]) / 3.0
                diff = max(abs(nnn-actual_status[u]), abs(nnn-actual_status[v]), abs(nnn-actual_status[z]))
                actual_status[u]=actual_status[v]=actual_status[z]=nnn
            else:
                diff = max(abs(nn-actual_status[u]), abs(nn-actual_status[v]), abs(nn-actual_status[z]))
                actual_status[u]=actual_status[v]=actual_status[z]=nn
        elif abs(actual_status[z]-actual_status[v])<eps:
            nn = (actual_status[z]+actual_status[v]) / 2.0
            if abs(actual_status[u]-nn) < eps:
                nnn = (actual_status[u]+actual_status[v]+actual_status[z]) / 3.0
                diff = max(abs(nnn-actual_status[u]), abs(nnn-actual_status[v]), abs(nnn-actual_status[z]))
                actual_status[u]=actual_status[v]=actual_status[z]=nnn
            else:
                diff = max(abs(nn-actual_status[u]), abs(nn-actual_status[v]), abs(nn-actual_status[z]))
                actual_status[u]=actual_status[v]=actual_status[z]=nn
        else:
            k = random.uniform(0.00001,0.9999)
            if k < self.params['model']['p']:
                diff = self.rewiring(nodes, actual_status, u, v, self.params['model']['epsilon'])
            else:
                diff = 0.0000001
        return diff


    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """

        actual_status = self.status.copy()

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(self.status)
            if node_status:
                return {"iteration": 0, "status": actual_status,
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": 0, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}

        n = self.graph.number_of_nodes()
        nodes = set(self.graph.nodes)
        max_diff = -1

        for i in range(0, n):
            k = random.uniform(0.00001,0.9999)

            n1 = int(choice(self.ids))

            if len(self.node_data) == 0:
                sts = self.sts
                ids = self.ids
                neigh_sts = np.delete(sts, n1)
                neigh_ids = np.delete(ids, n1)
            else:
                neigh_ids = self.graph.neighbors(n1)
                neigh_sts = np.array([actual_status[id] for id in neigh_ids])

            if len(neigh_sts) > 0:

                selection_prob = self.pb1(neigh_sts, actual_status[n1])

                # compute probabilities to select a second node among the neighbours
                total = np.sum(selection_prob)
                selection_prob = selection_prob / total
                cumulative_selection_probability = np.cumsum(selection_prob)

                r = np.random.random_sample()
                n2 = np.argmax(
                    cumulative_selection_probability >= r)
                n2 = int(neigh_ids[n2])

                n3 = self.select_triangle(actual_status, n1, n2, neigh_ids, self.params['model']['gamma'])

                if n3 > 0:
                    diff = self.peerpressure(nodes, actual_status, n1, n2, n3, self.params['model']['epsilon'])
                else:
                    diff = np.abs(actual_status[n1] - actual_status[n2])

                    if diff < self.params['model']['epsilon']:
                        avg = (actual_status[n1]+actual_status[n2])/2.0
                        actual_status[n1] = avg
                        actual_status[n2] = avg
                    else:
                        if k < self.params['model']['p']:
                            diff = self.rewiring(nodes, actual_status, n1, n2, self.params['model']['epsilon'])
                        else:
                            diff = -1
                    
                if diff > max_diff:
                    max_diff = diff

        delta = actual_status
        node_count = {}
        status_delta = {}

        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta,
                    "node_count": node_count.copy(), "status_delta": status_delta.copy(), "max_diff":max_diff}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy(),"max_diff":max_diff}

    def steady_state(self, max_iterations=100000, nsteady=1000, sensibility=0.00001, node_status=True,
                     progress_bar=False):
        """
        Execute a bunch of model iterations

        :param max_iterations: the maximum number of iterations to execute
        :param nsteady: number of required stable states
        :param sensibility: sensibility check for a steady state
        :param node_status: if the incremental node status has to be returned.
        :param progress_bar: whether to display a progress bar, default False

        :return: a list containing for each iteration a dictionary {"iteration": iteration_id, "status": dictionary_node_to_opinion}
        """
        system_status = []
        steady_it = 0
        for it in tqdm.tqdm(range(0, max_iterations), disable=not progress_bar):
            its = self.iteration(node_status)

            if it > 0:
                old = np.array(list(system_status[-1]['status'].values()))
                actual = np.array(list(its['status'].values()))

                if np.all((its['max_diff'] < sensibility)):
                    steady_it += 1
                else:
                    steady_it = 0

            system_status.append(its)
            if steady_it == nsteady:
                return system_status[:-nsteady]

        return system_status
    
    def steady_state_coevolving(self, max_iterations=1000000, nsteady=1000, sensibility=0.00001, node_status=True,
                        progress_bar=False):
            """
            Execute a bunch of model iterations

            :param max_iterations: the maximum number of iterations to execute
            :param nsteady: number of required stable states
            :param sensibility: sensibility check for a steady state
            :param node_status: if the incremental node status has to be returned.
            :param progress_bar: whether to display a progress bar, default False

            :return: a list containing for each iteration a dictionary {"iteration": iteration_id, "status": dictionary_node_to_status}
            """
            system_status = []
            steady_it = 0
            for it in tqdm.tqdm(range(0, max_iterations), disable=not progress_bar):
                
                oldgraph = self.graph.graph.copy()

                its = self.iteration(node_status)

                if it > 0:
                    # old = np.array(list(system_status[-1]['status'].values()))
                    # actual = np.array(list(its['status'].values()))
                    # res = np.abs(old - actual)
                    if np.all((its['max_diff'] < sensibility)):
                        steady_it += 1
                    else:
                        steady_it = 0

                system_status.append(its)

                if oldgraph.edges() != self.graph.graph.edges() : steady_it = 0 

                if steady_it == nsteady:
                    return system_status[:-nsteady]

            return system_status