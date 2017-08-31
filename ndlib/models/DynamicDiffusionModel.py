import abc
import warnings
import numpy as np
import past.builtins
import future.utils
import networkx as nx
from DiffusionModel import DiffusionModel

__author__ = "Giulio Rossetti"
__email__ = "giulio.rossetti@gmail.com"


class ConfigurationException(Exception):
    """Configuration Exception"""


class DynamicDiffusionModel(DiffusionModel):
    """
        Partial Abstract Class that defines Diffusion Models
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, graph):
        """
            Model Constructor

            :param graph: A networkx graph object
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
        self.dyngraph = graph
        self.graph = self.dyngraph
        self.status = {n: 0 for n in self.dyngraph.nodes()}
        self.initial_status = {}

        snapshot_ids = self.dyngraph.temporal_snapshots_ids()
        self.min_snapshot_id = min(snapshot_ids)
        self.max_snapshot_id = max(snapshot_ids)
        self.stream_execution = False

    def __validate_configuration(self, configuration):
        """
        Validate the consistency of a Configuration object for the specific model
        :param configuration: a Configuration object instance
        """

        # Checking mandatory parameters
        omp = set([k for k in self.parameters['model'].keys() if not self.parameters['model'][k]['optional']])
        onp = set([k for k in self.parameters['nodes'].keys() if not self.parameters['nodes'][k]['optional']])

        mdp = set(configuration.get_model_parameters().keys())
        ndp = set(configuration.get_nodes_configuration().keys())

        if len(omp) > 0:
            if len(omp & mdp) != len(omp):
                raise ConfigurationException(
                    {"message": "Missing mandatory model parameter(s)", "parameters": omp - mdp})

        if len(onp) > 0:
            if len(onp & ndp) != len(onp):
                raise ConfigurationException(
                    {"message": "Missing mandatory node parameter(s)", "parameters": onp - ndp})

        # Checking optional parameters
        omp = set([k for k in self.parameters['model'].keys() if self.parameters['model'][k]['optional']])
        onp = set([k for k in self.parameters['nodes'].keys() if self.parameters['nodes'][k]['optional']])

        if len(omp) > 0:
            for param in omp:
                if param not in mdp:
                    configuration.add_model_parameter(param, self.parameters['model'][param]['default'])

        if len(onp) > 0:
            for param in onp:
                if param not in ndp:
                    for nid in self.graph.nodes():
                        configuration.add_node_configuration(param, nid, self.parameters['nodes'][param]['default'])

        # Checking initial simulation status
        sts = set(configuration.get_model_configuration().keys())
        if self.discrete_state and "Infected" not in sts and "percentage_infected" not in mdp:
            warnings.warn('Initial infection missing: a random sample of 5% of graph nodes will be set as infected')
            self.params['model']["percentage_infected"] = 0.05

    def execute_snapshots(self, node_status=True):
        self.stream_execution = False
        system_status = []
        for t in past.builtins.xrange(self.min_snapshot_id, self.max_snapshot_id+1):
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
