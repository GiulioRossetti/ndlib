from ndlib.models.DiffusionModel import DiffusionModel
import networkx as nx
import numpy as np
import past.builtins
import tqdm

__author__ = ["Giulio Rossetti", "Valentina Pansanella"]
__email__ = ["giulio.rossetti@isti.cnr.it", "valentina.pansanella@sns.it"]

class ConfigurationException(Exception):
    """Configuration Exception"""

class SimilarityDrivenBCM(DiffusionModel):
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

        if not isinstance(graph, nx.DiGraph):
            raise ValueError("The graph must be a directed graph")

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
            },
            "nodes": {},
            "edges": {
                "mu":{
                    "descr": "learning parameter",
                    "range": [0,1],
                    "optional": False
                }
            }
        }

        self.name = "Similarity driven bounded confidence"
        self.node_data = {}
        self.ids = None
        self.sts = None
    
    def set_initial_status(self, configuration=None):
        """
        Override behaviour of methods in class DiffusionModel.
        Overwrites initial status using random real values.
        """
        super(SimilarityDrivenBCM, self).set_initial_status(configuration)

        try:
            for node in self.status:
                self.status[node] = np.random.random_sample()
            self.initial_status = self.status.copy()
        except:
            raise ConfigurationException("Initial opinion distribution not defined")
            
        nids = np.array(list(self.status.items()))
        self.ids = nids[:, 0].astype(int)

        for i in self.graph.nodes:
            i_neigh = list(self.graph.neighbors(i))
            i_ids = nids[:, 0][i_neigh]
            i_ids = i_ids.astype(int)
            i_sts = nids[:, 1][i_neigh]
            self.node_data[i] = (i_ids, i_sts)
    
    def get_status(self):
        return self.status
    
    def iteration(self, node_status=True):
        """
        Execute a single model iteration
        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        rng = np.random.default_rng()
        actual_status = self.status.copy()

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(self.status)
            d = {"iteration": 0, "status": actual_status, "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            if node_status:
                return d

        n = self.graph.number_of_nodes()
        for i in range(n):
            n1 = int(rng.choice(self.ids))
            neigh_ids = self.graph.neighbors(n1)
            while not np.any(neigh_ids):
                n1 = int(rng.choice(self.ids))
                neigh_ids = self.graph.neighbors(n1)
            n2 = int(rng.choice(neigh_ids))

            # update status of n1 and n2
            x_1 = actual_status[n1]
            x_2 = actual_status[n2] 
            diff = np.abs(x_1 - x_2)
            if diff < self.params['model']['epsilon']:
                actual_status[n1] = x_1 + self.params['edges']['mu'][(n1, n2)]*(x_2-x_1)
                if n1 in self.graph.neighbors(n2):
                    actual_status[n2] = x_2 + self.params['edges']['mu'][(n2, n1)]*(x_1-x_2)
                        
        # delta, node_count, status_delta = self.status_delta(actual_status)
        delta = actual_status
        node_count = {}
        status_delta = {}

        self.status = actual_status
        self.actual_iteration += 1

        d={"iteration": self.actual_iteration - 1, "status": delta, "node_count": node_count.copy(), "status_delta": status_delta.copy()}

        if node_status:
            return d


    def steady_state(self, max_iterations=100000, nsteady=1000, sensibility=0.00001, node_status=True,
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
        for it in tqdm.tqdm(list(range(0, max_iterations)), disable=not progress_bar):
            its = self.iteration(node_status)

            if it > 0:
                old = np.array(list(system_status[-1]['status'].values()))
                actual = np.array(list(its['status'].values()))
                res = np.abs(old - actual)
                if np.all((res < sensibility)):
                    steady_it += 1
                else:
                    steady_it = 0

            system_status.append(its)
            if steady_it == nsteady:
                return system_status[:-nsteady]

        return system_status


    def iteration_bunch(self, path, filename, bunch_size, node_status=True, progress_bar=False):
        """
        Execute a bunch of model iterations
        :param bunch_size: the number of iterations to execute
        :param node_status: if the incremental node status has to be returned.
        :param progress_bar: whether to display a progress bar, default False
        :return: a list containing for each iteration a dictionary {"iteration": iteration_id, "status": dictionary_node_to_status}
        """
        system_status = []
        for it in tqdm.tqdm(past.builtins.xrange(0, bunch_size), disable=not progress_bar):
            its = self.iteration(node_status)

            if it > 0:
                old = np.array(list(system_status[-1]['status'].values()))
                actual = np.array(list(its['status'].values()))
                res = np.abs(old - actual)
                
                if it % 10 == 0:
                    filename += f'_{it}.json.gz'
                    self.save_status(path, filename)
                    
            system_status = its

        return system_status
