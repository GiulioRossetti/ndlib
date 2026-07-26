import numpy as np
from ndlib.models.CompositeModel import CompositeModel
from ndlib.models.compartments.NodeStochastic import NodeStochastic
from ndlib.models.compartments.NodeThreshold import NodeThreshold
from ndlib.models.compartments.NodeCategoricalAttribute import NodeCategoricalAttribute
from ndlib.models.compartments.NodeNumericalAttribute import NodeNumericalAttribute
from ndlib.models.compartments.NodeNumericalVariable import NodeNumericalVariable
from ndlib.models.compartments.EdgeStochastic import EdgeStochastic
from ndlib.models.compartments.EdgeCategoricalAttribute import EdgeCategoricalAttribute
from ndlib.models.compartments.EdgeNumericalAttribute import EdgeNumericalAttribute
from ndlib.models.compartments.ConditionalComposition import ConditionalComposition
from ndlib.models.compartments.CountDown import CountDown
from ndlib.models.compartments.enums.NumericalType import NumericalType

class MajorityRuleStarter(CompositeModel):
    def __init__(self, graph, seed=None):
        # Bypass CompositeModel.__init__ to avoid recursion bug in super(self.__class__, self)
        from ndlib.models.DiffusionModel import DiffusionModel
        DiffusionModel.__init__(self, graph, seed=seed)
        self.available_statuses = {}
        self.compartment = {}
        self.compartment_progressive = 0
        self.status_progressive = 0
        self.name = 'MajorityRuleStarter'
        self.discrete_state = True
        self.available_statuses = {
            'Agree': 0,
            'Disagree': 1,
        }
        self.parameters = {
            'model': {
                'percentage_Agree': {
                    'descr': 'Initial percentage of Agree nodes',
                    'range': [0, 1],
                    'optional': True,
                    'default': 0.500000
                },
                'percentage_Disagree': {
                    'descr': 'Initial percentage of Disagree nodes',
                    'range': [0, 1],
                    'optional': True,
                    'default': 0.500000
                },
            },
            'nodes': {},
            'edges': {}
        }

        # Add statuses
        self.add_status('Agree')
        self.add_status('Disagree')

        # Define compartments
        stance_gate = NodeCategoricalAttribute(attribute='stance', value='majority', probability=1)
        support = NodeStochastic(rate=0.2, triggering_status='Agree')
        pushback = NodeStochastic(rate=0.2, triggering_status='Disagree')

        # Define rules
        self.add_rule('Disagree', 'Agree', pushback)

    def set_initial_status(self, configuration):
        configuration = configuration or None
        model_params = configuration.get_model_parameters() if configuration is not None else {}
        nodes_cfg = configuration.get_nodes_configuration() if configuration is not None else {}
        edges_cfg = configuration.get_edges_configuration() if configuration is not None else {}
        status_cfg = configuration.get_model_configuration() if configuration is not None else {}

        self.params['nodes'] = {}
        self.params['edges'] = {}
        self.params['status'] = {}
        self.params['model'] = {}

        for param, param_info in self.parameters['model'].items():
            self.params['model'][param] = model_params.get(param, param_info.get('default'))

        for param, node_to_value in nodes_cfg.items():
            if len(node_to_value) < len(self.graph.nodes):
                raise ValueError({'message': 'Not all nodes have a configuration specified'})
            self.params['nodes'][param] = node_to_value

        for param, edge_to_values in edges_cfg.items():
            if len(edge_to_values) == len(self.graph.edges):
                self.params['edges'][param] = {}
                for e in edge_to_values:
                    self.params['edges'][param][e] = edge_to_values[e]

        for status_name, nodes in status_cfg.items():
            self.params['status'][status_name] = nodes
            if status_name in self.available_statuses:
                for node in nodes:
                    self.status[node] = self.available_statuses[status_name]

        pcts = {}
        for status_name in self.available_statuses:
            param_key = 'percentage_%s' % status_name
            if param_key in self.params['model']:
                pcts[status_name] = float(self.params['model'][param_key])
        if pcts:
            nodes = list(self.graph.nodes)
            np.random.shuffle(nodes)
            current_idx = 0
            n_nodes = len(nodes)
            for status_name, pct in pcts.items():
                count = int(round(pct * n_nodes))
                end_idx = min(current_idx + count, n_nodes)
                for i in range(current_idx, end_idx):
                    self.status[nodes[i]] = self.available_statuses[status_name]
                current_idx = end_idx
            self.initial_status = self.status.copy()
        return self
