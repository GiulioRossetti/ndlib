from ndlib.models.DiffusionModel import DiffusionModel
import future.utils
import networkx as nx
import numpy as np
from scipy.sparse import csr_matrix
import psutil
import ray


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


## STEFANO: this is a first attempt at parallelizing the iteration
# num_cpus = psutil.cpu_count(logical=False)
# ray.shutdown()
# ray.init(num_cpus=num_cpus)

# @ray.remote
# def update(model, chunk):
#     actual_status = {}
#     for u in chunk:
#         u_status = self.status[u]
#         for i in range(0, self.compartment_progressive):
#             if u_status == self.available_statuses[self.compartment[i][0]]:
#                 rule = self.compartment[i][2]
#                 test = rule.execute(node=u, graph=self.graph, status=self.status,
#                                     status_map=self.available_statuses, params=self.params)
#                 if test:
#                     actual_status[u] = self.available_statuses[self.compartment[i][1]]
#                     break
#     return actual_status
#         changed = np.zeros(selif.graph.number_of_nodes(), dtype=bool)
        
#         for i in range(0, self.compartment_progressive):
#             rule = self.compartment[i][2]
#             test = rule.execute(self.adjacency, self.edges, self.attributes, params=self.params)
#             to_change = np.logical_and(self.status_array==self.available_statuses[self.compartment[i][0]], test, ~changed)
#             self.status_array = np.where(to_change, self.available_statuses[self.compartment[i][1]], self.status_array)
#             changed = np.logical_or(changed, to_change)
#             if np.all(changed):
#                 break

## STEFANO: NOVEL ARRAY BASED COMPARTMENT
class CompositeModelArray(DiffusionModel):

    def __init__(self, graph):
        """
             Model Constructor
             :param graph: A networkx graph object
         """
        super(self.__class__, self).__init__(graph)
        self.available_statuses = {}
        self.compartment = {}
        self.compartment_progressive = 0
        self.status_progressive = 1
        self.adjacency = nx.adjacency_matrix(graph,range(graph.number_of_nodes())) 
        self.edges = {}
        edge_attrs = set().union(*[e[2].keys() for e in graph.edges(data=True)])
        temp_d = {}
        for attr in edge_attrs:
            self.edges[attr] = {}
            temp_d[attr] = {}
            for idx,v in nx.get_edge_attributes(graph, attr).items():
                temp_d[attr].setdefault(v,[]).append(idx)
            for v,idxs in temp_d[attr].items():
                rows, cols = list(zip(*idxs))
                self.edges[attr][v] = csr_matrix((np.ones(len(idxs)),(rows,cols)), shape=self.adjacency.shape)
                self.edges[attr][v] = self.edges[attr][v]+self.edges[attr][v].T
        self.attributes = {}

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
        self.clean_initial_status(list(self.available_statuses.values()))
        actual_status = {node:nstatus for node,nstatus in self.status.items()}

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(actual_status)
            self.status_array = np.array([v for k,v in sorted(self.status.items())])
            # self.adjacency = self.adjacency.multiply(self.status_array) 
            if node_status:
                return {"iteration": 0, "status": actual_status.copy(),
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": 0, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}

        changed = np.zeros(self.graph.number_of_nodes(), dtype=bool)
        for i in range(0, self.compartment_progressive):
            rule = self.compartment[i][2]
            test = rule.execute(self.adjacency.multiply(self.status_array), self.edges, self.attributes, self.available_statuses, params=self.params)
            test = np.array(test).reshape(self.graph.number_of_nodes())
            to_change = np.logical_and(self.status_array==self.available_statuses[self.compartment[i][0]], test, ~changed)
            self.status_array = np.where(to_change, self.available_statuses[self.compartment[i][1]], self.status_array)
            changed = np.logical_or(changed, to_change)
            if np.all(changed):
                break
        actual_status = {i:v for i,v in enumerate(list(self.status_array))}

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
