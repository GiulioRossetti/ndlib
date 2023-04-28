from ndlib.models.DiffusionModel import DiffusionModel
import numpy as np
import tqdm
import random
import time


class AlgorithmicBiasMediaModel(DiffusionModel):
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

        self.available_statuses = {"Infected": 0}

        self.parameters = {
            "model": {
                "epsilon": {
                    "descr": "Bounded confidence threshold",
                    "range": [0, 1],
                    "optional": False,
                },
                "gamma": {
                    "descr": "Algorithmic bias",
                    "range": [0, 100],
                    "optional": False,
                },
                "gamma_media": {
                    "descr": "Bias with media",
                    "range": [0, 100],
                    "optional": False,
                },
                "p": {
                    "descr": "Probability of media interaction",
                    "range": [0, 1],
                    "optional": False,
                },
                "k": {
                    "descr": "number of media",
                    "range": [0, self.graph.number_of_nodes],
                    "optional": False,
                },
            },
            "nodes": {},
            "edges": {},
        }

        self.name = "Agorithmic Bias Media"

        self.node_data = {}
        self.ids = None
        self.sts = None
        self.stsmedia = None

    def set_initial_status(self, configuration=None):
        """
        Override behaviour of methods in class DiffusionModel.
        Overwrites initial status using random real values.
        """
        super(AlgorithmicBiasMediaModel, self).set_initial_status(configuration)

        # set node status
        for node in self.status:
            self.status[node] = np.random.random_sample()
        self.initial_status = self.status.copy()

        ### Initialization numpy representation

        max_edgees = (
            self.graph.number_of_nodes() * (self.graph.number_of_nodes() - 1)
        ) / 2
        nids = np.array(list(self.status.items()))
        self.ids = nids[:, 0]

        max_edgees = (
            self.graph.number_of_nodes() * (self.graph.number_of_nodes() - 1)
        ) / 2
        nids = np.array(list(self.status.items()))
        self.ids = nids[:, 0]

        if max_edgees == self.graph.number_of_edges():
            self.sts = nids[:, 1]

        else:
            for i in self.graph.nodes:
                i_neigh = list(self.graph.neighbors(i))
                i_ids = nids[:, 0][i_neigh]
                i_sts = nids[:, 1][i_neigh]
                self.node_data[i] = (i_ids, i_sts)

        self.stsmedia = np.random.rand(self.params["model"]["k"])
        self.steady = 0
        self.currentit = 0

    def set_media_opinions(self, opinions_list):
        if len(opinions_list) != self.params["model"]["k"]:
            print("list must be of length {}".format(self.params["model"]["k"]))
            return
        self.stsmedia = np.array(opinions_list)

    @staticmethod
    def prob(distance, gamma, min_dist):
        if distance < min_dist:
            distance = min_dist
        return np.power(distance, -gamma)

    def pb1(self, statuses, i_status):
        dist = np.abs(statuses - i_status)
        null = np.full(statuses.shape[0], 0.00001)
        max_base = np.maximum(dist, null)
        dists = max_base ** -self.params["model"]["gamma"]
        return dists

    def pb2(self, statuses, i_status):
        dist = np.abs(statuses - i_status)
        null = np.full(statuses.shape[0], 0.00001)
        max_base = np.maximum(dist, null)
        dists = max_base ** -self.params["model"]["gamma_media"]
        return dists

    def iteration(self, node_status=True):

        actual_status = self.status.copy()

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(self.status)
            if node_status:
                return {
                    "iteration": 0,
                    "status": actual_status,
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

        n = self.graph.number_of_nodes()

        # interact with peers
        for n1 in range(0, n):

            if len(self.node_data) == 0:
                sts = self.sts
                ids = self.ids
                neigh_sts = np.delete(sts, n1)
                neigh_ids = np.delete(ids, n1)
            else:
                neigh_ids = self.node_data[n1][0]
                neigh_sts = np.array([actual_status[id] for id in neigh_ids])

            # selection_prob = self.pb1(sts, self.status[n1])
            selection_prob = self.pb1(neigh_sts, actual_status[n1])

            # compute probabilities to select a second node among the neighbours
            total = np.sum(selection_prob)
            selection_prob = selection_prob / total
            cumulative_selection_probability = np.cumsum(selection_prob)

            r = np.random.random_sample()
            n2 = np.argmax(cumulative_selection_probability >= r)
            n2 = int(neigh_ids[n2])

            # update status of n1 and n2
            diff = np.abs(actual_status[n1] - actual_status[n2])

            if diff < self.params["model"]["epsilon"]:
                avg = (actual_status[n1] + actual_status[n2]) / 2.0
                actual_status[n1] = avg
                actual_status[n2] = avg

                if len(self.node_data) == 0:
                    self.sts[n1] = avg
                    self.sts[n2] = avg

            if random.random() < self.params["model"]["p"]:
                selection_prob = self.pb2(self.stsmedia, actual_status[n1])
                total = np.sum(selection_prob)
                selection_prob = selection_prob / total
                cumulative_selection_probability = np.cumsum(selection_prob)
                r = np.random.random_sample()
                media = np.argmax(cumulative_selection_probability >= r)
                diff = np.abs(actual_status[n1] - self.stsmedia[media])
                if diff < self.params["model"]["epsilon"]:
                    avg = (actual_status[n1] + self.stsmedia[media]) / 2.0
                    actual_status[n1] = avg
                    if len(self.node_data) == 0:
                        self.sts[n1] = avg

        delta = actual_status
        node_count = {}
        status_delta = {}

        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {
                "iteration": self.actual_iteration - 1,
                "status": delta,
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

    def steady_state(
        self,
        max_iterations=10000000,
        nsteady=1000,
        sensibility=0.00001,
        node_status=True,
        progress_bar=False,
        drop_evolution=True,
    ):

        start = time.time()

        system_status = []
        steady_it = 0

        for it in tqdm.tqdm(range(0, max_iterations), disable=not progress_bar):

            its = self.iteration(node_status)

            if it > 0:
                old = np.array(list(system_status[-1]["status"].values()))
                actual = np.array(list(its["status"].values()))
                res = np.abs(old - actual)
                if np.all((res < sensibility)):
                    steady_it += 1
                else:
                    steady_it = 0

                if drop_evolution:
                    system_status = []

            system_status.append(its)

            if steady_it == nsteady:
                if drop_evolution:
                    return system_status
                else:
                    return system_status[:-nsteady]

        end = time.time()

        return system_status
