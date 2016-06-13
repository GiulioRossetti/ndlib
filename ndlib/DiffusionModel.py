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

        for n in self.graph.nodes():

            if configuration is not None and'nodes' in configuration and 'threshold' in configuration['nodes']:
                if len(configuration['nodes']['threshold']) < len(self.graph.nodes()):
                    raise Exception

                self.params['nodes']['threshold'][int(n)] = configuration['nodes']['threshold'][str(n)]
            else:
                self.params['nodes']['threshold'][int(n)] = np.random.random_sample()

            if configuration is not None and 'nodes' in configuration and 'profile' in configuration['nodes']:
                if len(configuration['nodes']['profile']) < len(self.graph.nodes()):
                    raise Exception

                self.params['nodes']['profile'][int(n)] = configuration['nodes']['profile'][str(n)]
            else:
                self.params['nodes']['profile'][int(n)] = np.random.random_sample()

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
        sampled_nodes = np.random.choice(self.status.keys(), number_of_initial_infected, replace=False)

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
                    self.status[node] = 1
                self.initial_status = self.status
                return

            elif 'percentage_infected' in configuration['model']:
                percentage_infected = configuration['model']['percentage_infected']

        for k in self.status:
            rnd = np.random.random_sample()
            if rnd <= percentage_infected:
                self.status[k] = 1
        self.initial_status = self.status

    def iteration_bunch(self, bunch_size):
        system_status = []
        # iterator = self.iteration()
        for it in xrange(0, bunch_size):
            itd, status = self.iteration()
            # itd, status = iterator.next()
            iteration = {"iteration": itd, "status": status}
            system_status.append(iteration)
        return system_status

    def complete_run(self):
        system_status = []
        previous_status = {}

        confidence = 2

        while True:

            if confidence == 0:
                break

            itd, status = self.iteration()
            iteration = {"iteration": itd, "status": status}

            flag = self.check_status_similarity(status, previous_status)
            previous_status = status

            if flag:
                confidence -= 1

            system_status.append(iteration)

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
