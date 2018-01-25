import abc
import past.builtins
import networkx as nx
from ndlib.models.DiffusionModel import DiffusionModel
import six

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

    iteration_bunch = execute_snapshots
