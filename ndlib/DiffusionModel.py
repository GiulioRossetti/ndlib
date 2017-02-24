import abc
import numpy as np

__author__ = "Giulio Rossetti"
__email__ = "giulio.rossetti@gmail.com"


class DiffusionModel(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, graph, params=None):
        """

        :rtype: object
        """
        self.params = {
            'nodes': {'threshold': {}, 'profile': {}},
            'edges': {},
            'model': {'percentage_infected': 0, 'infected_nodes': []}
        }

        # Set model specific global parameters
        if params is not None:
            for k, v in params.iteritems():
                self.params[k] = v

        self.actual_iteration = 0
        self.graph = graph
        self.status = {n: 0 for n in self.graph.nodes()}
        self.initial_status = {}

    def set_initial_status(self, configuration=None):
        """
        Set initial configuration of nodes (thresholds and profile) and edges (weight) as well as
        the initial status of the network, i.e., percentage of infected nodes or list of infected nodes.

        :param configuration: a dictionary of the form (it can be partially specified):
                            {
                            'nodes':
                                {
                                'threshold': {node1: value1, node2: value2, node3: value3},
                                'profile': {node1: value1, node2: value2, node3: value3}
                                },
                            'edges':
                                [
                                    {
                                    'source': node1,
                                    'target': node2,
                                    'weight': value
                                    },
                                    {
                                    'source': node2,
                                    'target': node3,
                                    'weight': value
                                     }
                                ]
                            'model':
                                {
                                'percentage_infected': value,
                                'infected_nodes': [node1, node2]
                                }
                            }

        """

        # Set additional node information

        if configuration is not None and 'nodes' in configuration and 'threshold' in configuration['nodes']:
            if len(configuration['nodes']['threshold']) < len(self.graph.nodes()):
                raise Exception
            self.params['nodes']['threshold'] = configuration['nodes']['threshold']
        else:
            for n in self.graph.nodes():
                self.params['nodes']['threshold'][n] = np.random.random_sample()

        if configuration is not None and 'nodes' in configuration and 'profile' in configuration['nodes']:
            if len(configuration['nodes']['profile']) < len(self.graph.nodes()):
                raise Exception
            self.params['nodes']['profile'] = configuration['nodes']['profile']
        else:
            for n in self.graph.nodes():
                self.params['nodes']['profile'][n] = np.random.random_sample()

        # Set additional edges information
        if configuration is not None and 'edges' in configuration:
            if len(configuration['edges']) == len(self.graph.edges()):
                for e in configuration['edges']:
                    u = e['source']
                    v = e['target']
                    w = e['weight']
                    self.params['edges'][(u, v)] = w

        # Set model additional information
        percentage_infected = 0.1
        if configuration is not None and 'model' in configuration:

            if 'infected_nodes' in configuration['model']:
                self.params['model']['infected_nodes'] = configuration['model']['infected_nodes']
                for node in self.params['model']['infected_nodes']:
                    self.status[node] = 1
                self.initial_status = self.status
                return

            elif 'percentage_infected' in configuration['model']:
                percentage_infected = configuration['model']['percentage_infected']
                self.params['model']['percentage_infected'] = percentage_infected
            else:
                self.params['model']['percentage_infected'] = percentage_infected

        number_of_initial_infected = len(self.graph.nodes()) * percentage_infected
        sampled_nodes = np.random.choice(self.status.keys(), int(number_of_initial_infected), replace=False)

        for k in sampled_nodes:
            self.status[k] = 1

        self.initial_status = self.status

    def change_initial_status(self, configuration):

        # Clean current status
        self.status = {node: 0 for node in self.graph.nodes()}
        percentage_infected = 0.1
        if configuration is not None and 'model' in configuration:

            if 'infected_nodes' in configuration['model']:
                self.params['model']['infected_nodes'] = configuration['model']['infected_nodes']
                for node in self.params['model']['infected_nodes']:
                    self.status[int(node)] = 1
                self.initial_status = self.status

            elif 'percentage_infected' in configuration['model']:
                percentage_infected = configuration['model']['percentage_infected']

            if 'blocked' in configuration['model']:
                for node in configuration['model']['blocked']:
                    self.status[int(node)] = -1
                self.initial_status = self.status

        if 1 not in set(self.initial_status.values()):
            subs = {n: s for n, s in self.initial_status.iteritems() if s != -1}
            for k in subs:
                rnd = np.random.random_sample()
                if rnd <= percentage_infected:
                    self.status[int(k)] = 1
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
        info = {k: v for k, v in self.params.iteritems() if k != 'nodes' and k != 'edges' and k != 'model'}
        if len(self.params['model']['infected_nodes']) > 0:
            info['selected_initial_infected'] = True
        else:
            info['selected_initial_infected'] = False
            info['percentage_infected_nodes'] = self.params['model']['percentage_infected']
        return info

    def reset(self):
        self.actual_iteration = 0
        self.status = self.initial_status

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
