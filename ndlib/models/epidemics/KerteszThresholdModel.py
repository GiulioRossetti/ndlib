from ..DiffusionModel import DiffusionModel
import networkx as nx
import numpy as np
from scipy import stats

__author__ = "Letizia Milli"
__email__ = "letizia.milli@di.unipi.it"


class KerteszThresholdModel(DiffusionModel):
    """
    Implements the blocked-nodes threshold model by Karsai et al.
    Model Parameters:
    (1) list of blocked nodes
    (2) exogenous adopter rate
    (3) node thresholds
    """

    def __init__(self, graph):
        super(self.__class__, self).__init__(graph)
        self.available_statuses = {
            "Susceptible": 0,
            "Infected": 1,
            "Blocked": -1
        }

        self.parameters = {
            "model": {
                "adopter_rate": {
                    "descr": "Exogenous adoption rate",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
                "percentage_blocked": {
                    "descr": "Percentage of blocked nodes",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.1
                }
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

        self.name = "Kertesz Threhold"

    def iteration(self):
        """

        """
        self.clean_initial_status(self.available_statuses.values())
        actual_status = {node: nstatus for node, nstatus in self.status.iteritems()}

        if self.actual_iteration == 0:
            if min(actual_status.values()) == 0:
                number_node_blocked = int(float(self.graph.number_of_nodes()) *
                                          float(self.params['model']['percentage_blocked']))

                i = 0
                while i < number_node_blocked:
                    # select a random node
                    node = self.graph.nodes()[np.random.randint(0, self.graph.number_of_nodes())]

                    # node not infected
                    if actual_status[node] == 0:

                        # node blocked
                        actual_status[node] = -1
                        self.status[node] = -1
                        i += 1

            self.actual_iteration += 1
            return 0, actual_status

        for node in self.graph.nodes():
            if self.status[node] != -1:
                xk = (0, 1)
                pk = (1-self.params['model']['adopter_rate'], self.params['model']['adopter_rate'])
                probability = stats.rv_discrete(name='probability', values=(xk, pk))
                number_probability = probability.rvs()

                if number_probability == 1:
                    actual_status[node] = 1
                else:
                    neighbors = self.graph.neighbors(node)
                    if isinstance(self.graph, nx.DiGraph):
                        neighbors = self.graph.predecessors(node)

                    infected = 0
                    for v in neighbors:
                        infected += self.status[v]

                    if len(neighbors) > 0:
                        infected_ratio = float(infected)/len(neighbors)
                        if infected_ratio >= self.params['nodes']['threshold'][node]:
                            actual_status[node] = 1

        delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        return self.actual_iteration-1, delta
