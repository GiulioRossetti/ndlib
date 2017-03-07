import abc
import numpy as np

__author__ = "Giulio Rossetti"
__email__ = "giulio.rossetti@gmail.com"


class DiffusionModel(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, graph):
        """

        :rtype: object
        """
        self.params = {
            'nodes': {},
            'edges': {},
            'model': {},
            'status': {}
        }

        self.available_statuses = {
            "Susceptible": 0,
            "Infected": 1,
            "Recovered": 2,
            "Blocked": -1
        }

        self.name = ""

        self.parameters = {}

        self.actual_iteration = 0
        self.graph = graph
        self.status = {n: 0 for n in self.graph.nodes()}
        self.initial_status = {}

    def set_initial_status(self, configuration):

        nodes_cfg = configuration.get_nodes_configuration()
        # Set additional node information

        for param, node_to_value in nodes_cfg.iteritems():
            if len(node_to_value) < len(self.graph.nodes()):
                raise Exception
            self.params['nodes'][param] = node_to_value

        edges_cfg = configuration.get_edges_configuration()
        # Set additional edges information
        for param, edge_to_values in edges_cfg.iteritems():
            if len(edge_to_values) == len(self.graph.edges()):
                self.params['edges'][param] = {}
                for e in edge_to_values:
                    self.params['edges'][param][e] = edge_to_values[e]

        # Set initial status
        model_status = configuration.get_model_configuration()

        for param, nodes in model_status.iteritems():
            self.params['status'][param] = nodes
            for node in nodes:
                self.status[node] = self.available_statuses[param]

        # Set model additional information
        model_params = configuration.get_model_parameters()
        for param, val in model_params.iteritems():
            self.params['model'][param] = val

        # Handle initial infection
        if 'infected_nodes' not in self.params['status']:
            if 'percentage_infected' not in model_params:
                percentage_infected = 0.1
                self.params['model']['percentage_infected'] = percentage_infected

            number_of_initial_infected = len(self.graph.nodes()) * self.params['model']['percentage_infected']
            available_nodes = [n for n in self.status if self.status[n] == 0]
            sampled_nodes = np.random.choice(available_nodes, int(number_of_initial_infected), replace=False)
            for k in sampled_nodes:
                self.status[k] = self.available_statuses['Infected']

        self.initial_status = self.status

    def clean_initial_status(self, valid_status=None):
        for n, s in self.status.iteritems():
            if s not in valid_status:
                self.status[n] = 0

    def iteration_bunch(self, bunch_size):
        system_status = []
        for it in xrange(0, bunch_size):
            itd, status = self.iteration()
            system_status.append({"iteration": itd, "status": status.copy()})
        return system_status

    def getinfo(self):
        info = {k: v for k, v in self.params.iteritems() if k not in ['nodes', 'edges', 'status']}
        if 'infected_nodes' in self.params['status']:
            info['selected_initial_infected'] = True
        return info['model']

    def reset(self):
        self.actual_iteration = 0
        self.status = self.initial_status

    def get_model_parameters(self):
        return self.parameters

    def get_name(self):
        return self.name

    @abc.abstractmethod
    def iteration(self):
        pass

    @staticmethod
    def check_status_similarity(actual, previous):
        for n, v in actual.iteritems():
            if n not in previous:
                return False
            if previous[n] != actual[n]:
                return False
        return True

    def status_delta(self, actual_status):
        delta = {}
        for n, v in self.status.iteritems():
            if v != actual_status[n]:
                delta[n] = actual_status[n]
        return delta
