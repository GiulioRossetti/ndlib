import abc
import numpy as np

__author__ = "Giulio Rossetti"
__email__ = "giulio.rossetti@gmail.com"


class ConfigurationException(Exception):
    """Raise for my specific kind of exception"""


class DiffusionModel(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, graph):
        """

        :rtype: object
        """
        self.discrete_state = True

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

        self.parameters = {
            "model": {},
            "nodes": {},
            "edges": {}
        }

        self.actual_iteration = 0
        self.graph = graph
        self.status = {n: 0 for n in self.graph.nodes()}
        self.initial_status = {}

    def __validate_configuration(self, configuration):

        # Checking mandatory parameters
        omp = set([k for k in self.parameters['model'].keys() if not self.parameters['model'][k]['optional']])
        onp = set([k for k in self.parameters['nodes'].keys() if not self.parameters['nodes'][k]['optional']])
        oep = set([k for k in self.parameters['edges'].keys() if not self.parameters['edges'][k]['optional']])

        mdp = set(configuration.get_model_parameters().keys())
        ndp = set(configuration.get_nodes_configuration().keys())
        edp = set(configuration.get_edges_configuration().keys())

        if len(omp) > 0:
            if len(omp & mdp) != len(omp):
                raise ConfigurationException({"message": "Missing mandatory model parameter(s)", "parameters": omp-mdp})

        if len(onp) > 0:
            if len(onp & ndp) != len(onp):
                raise ConfigurationException({"message": "Missing mandatory node parameter(s)", "parameters": onp-ndp})

        if len(oep) > 0:
            if len(oep & edp) != len(oep):
                raise ConfigurationException({"message": "Missing mandatory edge parameter(s)", "parameters": oep-edp})

        # Checking optional parameters
        omp = set([k for k in self.parameters['model'].keys() if self.parameters['model'][k]['optional']])
        onp = set([k for k in self.parameters['nodes'].keys() if self.parameters['nodes'][k]['optional']])
        oep = set([k for k in self.parameters['edges'].keys() if self.parameters['edges'][k]['optional']])

        if len(omp) > 0:
            for param in omp:
                if param not in mdp:
                    configuration.add_model_parameter(param, self.parameters['model'][param]['default'])

        if len(onp) > 0:
            for param in onp:
                if param not in ndp:
                    for nid in self.graph.nodes():
                        configuration.add_node_configuration(param, nid, self.parameters['nodes'][param]['default'])

        if len(oep) > 0:
            for param in oep:
                if param not in edp:
                    for eid in self.graph.edges():
                        configuration.add_edge_configuration(param, eid, self.parameters['edges'][param]['default'])

        # Checking initial simulation status
        sts = set(configuration.get_model_configuration().keys())
        if self.discrete_state and "Infected" not in sts and "percentage_infected" not in mdp:
            raise ConfigurationException({"message": "Missing mandatory initial infection status",
                                          "parameters": "percentage_infected"})

    def set_initial_status(self, configuration):

        self.__validate_configuration(configuration)

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
        if 'Infected' not in self.params['status']:
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

    def get_status_map(self):
        return self.available_statuses

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
