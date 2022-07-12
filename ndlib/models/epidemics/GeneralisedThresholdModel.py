from ..DiffusionModel import DiffusionModel
import future.utils
import random
import queue
from collections import defaultdict


__author__ = "Letizia Milli"
__license__ = "BSD-2-Clause"
__email__ = "letizia.milli@isti.cnr.it"


class GeneralisedThresholdModel(DiffusionModel):
    """
        Node Parameters to be specified via ModelConfig
       :param threshold: The node threshold. If not specified otherwise a value of 0.1 is assumed for all nodes.
    """

    def __init__(self, graph, seed=None):
        """
             Model Constructor
             :param graph: A networkx graph object
         """
        super(self.__class__, self).__init__(graph, seed)
        self.available_statuses = {
            "Susceptible": 0,
            "Infected": 1
        }

        self.parameters = {
            "model": {
                "tau": {
                    "descr": "Adoption threshold rate",
                    "range": [0, float("inf")],
                    "optional": False},
                "mu": {
                    "descr": "Exogenous timescale",
                    "range": [0, float("inf")],
                    "optional": False},
            },
            "nodes": {
                "threshold": {
                    "descr": "Node threshold",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.1
                }
            },
            "edges": {},
        }

        self.queue = queue.PriorityQueue()
        self.inqueue = defaultdict(int)

        self.name = "GeneralisedThresholdModel"

    def iteration(self, node_status=True):
        """
        Execute a single model iteration
        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        self.clean_initial_status(self.available_statuses.values())

        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            self.params['model']['queue'] = dict()
            return 0, actual_status

        gamma = float(self.params['model']['mu']) * float(self.actual_iteration) / float(self.params['model']['tau'])
        list_node = self.graph.nodes
        start = min(list_node)
        stop = max(list_node)
        number_node_susceptible = len(self.graph.nodes) - sum(self.status.values())

        while gamma >= 1 and number_node_susceptible >= 1:
            random_index = random.randrange(start, stop+1, 1)
            if random_index in list_node and actual_status[random_index] == 0:
                actual_status[random_index] = 1
                gamma -= 1
                number_node_susceptible -= 1

        for u in self.graph.nodes:
            if actual_status[u] == 1:
                continue

            neighbors = list(self.graph.neighbors(u))
            if self.graph.directed:
                neighbors = list(self.graph.predecessors(u))

            infected = 0
            for v in neighbors:
                infected += self.status[v]

            if len(neighbors) > 0:
                infected_ratio = float(infected)/len(neighbors)
                if infected_ratio >= self.params['nodes']['threshold'][u]:
                    if u not in self.inqueue:
                        self.queue.put((self.actual_iteration, u))
                        self.inqueue[u] = None

        while not self.queue.empty():
            next = self.queue.queue[0]
            if self.actual_iteration - next[0] >= self.params['model']['tau']:
                self.queue.get()
            else:
                break

        delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        return self.actual_iteration - 1, delta
