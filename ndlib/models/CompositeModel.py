from ndlib.models.DiffusionModel import DiffusionModel
import future.utils

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class CompositeModel(DiffusionModel):

    def __init__(self, graph):
        """
             Model Constructor
             :param graph: A networkx graph object
         """
        super(self.__class__, self).__init__(graph)
        self.available_statuses = {}
        self.compartment = {}
        self.compartment_progressive = 0
        self.status_progressive = 0

    def add_status(self, status_name):
        if status_name not in self.available_statuses:
            self.available_statuses[status_name] = self.status_progressive
            self.status_progressive += 1

    def add_rule(self, status_from, status_to, rule):
        self.compartment[self.compartment_progressive] = (status_from, status_to, rule)
        self.compartment_progressive += 1

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        self.clean_initial_status(self.available_statuses.values())
        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(actual_status)
            if node_status:
                return {"iteration": 0, "status": actual_status.copy(),
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": 0, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}

        for u in self.graph.nodes:
            u_status = self.status[u]
            for i in range(0, self.compartment_progressive):

                if u_status == self.available_statuses[self.compartment[i][0]]:
                    rule = self.compartment[i][2]
                    test = rule.execute(node=u, graph=self.graph, status=self.status,
                                        status_map=self.available_statuses, params=self.params)
                    if test:
                        actual_status[u] = self.available_statuses[self.compartment[i][1]]
                        break

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
