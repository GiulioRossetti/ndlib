import abc
import past.builtins
import networkx as nx
from ndlib.models.DiffusionModel import DiffusionModel
import six
import warnings
import numpy as np
import future.utils

__author__ = "Giulio Rossetti"
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class ConfigurationException(Exception):
    """Configuration Exception"""


@six.add_metaclass(abc.ABCMeta)
class DynamicDiffusionModel(DiffusionModel):
    """
        Partial Abstract Class that defines Diffusion Models
    """
    # __metaclass__ = abc.ABCMeta

    def __init__(self, graph, seed=None):
        """
            Model Constructor

            :param graph: A networkx graph object
        """

        np.random.seed(seed)

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
        self.dyngraph = graph
        self.graph = self.dyngraph
        self.status = {n: 0 for n in self.dyngraph.nodes()}
        self.initial_status = {}

        snapshot_ids = self.dyngraph.temporal_snapshots_ids()
        self.min_snapshot_id = min(snapshot_ids)
        self.max_snapshot_id = max(snapshot_ids)
        self.stream_execution = False

    def execute_snapshots(self, bunch_size=None, node_status=True):
        self.stream_execution = False
        if bunch_size is None:
            bunch_size = self.max_snapshot_id+1
        if bunch_size > self.max_snapshot_id+1:
            raise ValueError("Number of iterations required greater than snapshot number.")
        system_status = []
        for t in past.builtins.xrange(self.min_snapshot_id, bunch_size):
            self.graph = self.dyngraph.time_slice(t_from=t)
            its = self.iteration(node_status)
            system_status.append(its)
        return system_status

    def execute_iterations(self, node_status=True):
        self.stream_execution = True
        system_status = []
        for e in self.dyngraph.stream_interactions():
            if e[2] == '+':
                self.graph = nx.Graph()
                self.graph.add_edge(e[0], e[1])
                its = self.iteration(node_status)
                system_status.append(its)
        return system_status

    def set_initial_status(self, configuration):
        """
        Set the initial model configuration

        :param configuration: a ```ndlib.models.ModelConfig.Configuration``` object
        """

        self.__validate_configuration(configuration)

        nodes_cfg = configuration.get_nodes_configuration()
        # Set additional node information

        for param, node_to_value in future.utils.iteritems(nodes_cfg):
            if len(node_to_value) < len(self.graph.nodes()):
                raise ConfigurationException({"message": "Not all nodes have a configuration specified"})

            self.params['nodes'][param] = node_to_value

        edges_cfg = configuration.get_edges_configuration()
        # Set additional edges information
        for param, edge_to_values in future.utils.iteritems(edges_cfg):
            if len(edge_to_values) == len(self.graph.edges()):
                self.params['edges'][param] = {}
                for e in edge_to_values:
                    self.params['edges'][param][e] = edge_to_values[e]

        # Set initial status
        model_status = configuration.get_model_configuration()

        for param, nodes in future.utils.iteritems(model_status):
            self.params['status'][param] = nodes
            for node in nodes:
                self.status[node] = self.available_statuses[param]

        # Set model additional information
        model_params = configuration.get_model_parameters()
        for param, val in future.utils.iteritems(model_params):
            self.params['model'][param] = val

        # Handle initial infection
        if 'Infected' not in self.params['status']:
            if 'percentage_infected' in self.params['model']:
                number_of_initial_infected = len(self.graph.nodes()) * float(self.params['model']['percentage_infected'])
                if number_of_initial_infected < 1:
                    warnings.warn('Graph with less than 100 nodes: a single node will be set as infected')
                    number_of_initial_infected = 1

                available_nodes = [n for n in self.status if self.status[n] == 0]
                sampled_nodes = np.random.choice(available_nodes, int(number_of_initial_infected), replace=False)
                for k in sampled_nodes:
                    self.status[k] = self.available_statuses['Infected']

        self.initial_status = self.status

    def __validate_configuration(self, configuration):
        """
        Validate the consistency of a Configuration object for the specific model

        :param configuration: a Configuration object instance
        """
        if "Infected" not in self.available_statuses:
            raise ConfigurationException("'Infected' status not defined.")

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
            warnings.warn('Initial infection missing: a random sample of 5% of graph nodes will be set as infected')
            self.params['model']["percentage_infected"] = 0.05

    iteration_bunch = execute_snapshots
