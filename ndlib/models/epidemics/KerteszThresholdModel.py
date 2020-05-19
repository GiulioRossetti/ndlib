from ..DiffusionModel import DiffusionModel
import numpy as np
from scipy import stats
import future.utils

__author__ = "Letizia Milli"
__license__ = "BSD-2-Clause"
__email__ = "letizia.milli@di.unipi.it"


class KerteszThresholdModel(DiffusionModel):
    """
         Node/Model Parameters to be specified via ModelConfig

        :param threshold: The node threshold. As default a value of 0.1 is assumed for all nodes.
        :param adopter_rate: The probability of spontaneous adoptions. Defaults value 0.
        :param fraction_infected: The percentage of blocked nodes. Default value 0.1.
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

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        self.clean_initial_status(self.available_statuses.values())
        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        if self.actual_iteration == 0:

            if min(actual_status.values()) == 0:
                number_node_blocked = int(float(self.graph.number_of_nodes()) *
                                          float(self.params['model']['percentage_blocked']))

                i = 0
                while i < number_node_blocked:
                    # select a random node
                    #print("aa", len(self.graph.nodes()))#, self.graph.number_of_nodes(), np.random.randint(0, self.graph.number_of_nodes()))
                    try:
                        node = list(self.graph.nodes())[np.random.randint(0, self.graph.number_of_nodes())]

                        # node not infected
                        if actual_status[node] == 0:

                            # node blocked
                            actual_status[node] = -1
                            self.status[node] = -1
                            i += 1
                    except:
                        i += 1

            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(actual_status)
            if node_status:
                return {"iteration": 0, "status": actual_status.copy(),
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": 0, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}

        for node in self.graph.nodes:
            if self.status[node] == 0:
                if self.params['model']['adopter_rate'] > 0:
                    xk = (0, 1)
                    pk = (1-self.params['model']['adopter_rate'], self.params['model']['adopter_rate'])
                    probability = stats.rv_discrete(name='probability', values=(xk, pk))
                    number_probability = probability.rvs()

                    if number_probability == 1:
                        actual_status[node] = 1
                        continue

                neighbors = list(self.graph.neighbors(node))
                if len(neighbors) == 0:
                    continue

                if self.graph.directed:
                    neighbors = self.graph.predecessors(node)

                infected = 0
                for v in neighbors:
                    if self.status[v] != -1:
                        infected += self.status[v]

                infected_ratio = float(infected)/len(neighbors)
                if infected_ratio >= self.params['nodes']['threshold'][node]:
                    actual_status[node] = 1

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
