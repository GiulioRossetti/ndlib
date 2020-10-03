from __future__ import absolute_import

import unittest
import os
import networkx as nx
import numpy as np
import ndlib.models.ModelConfig as mc
import ndlib.models.ContinuousModel as gc
import ndlib.models.ContinuousModelRunner as gcr
import ndlib.models.compartments as cpm
from ndlib.models.compartments.enums.NumericalType import NumericalType

__author__ = 'Mathijs Maijer'
__license__ = "BSD-2-Clause"
__email__ = "m.f.maijer@gmail.com"

class NdlibContinuousModelTest(unittest.TestCase):
    def test_bare_model(self):
        def initial_addiction(node, graph, status, constants):
            addiction = 0
            return addiction

        def initial_self_confidence(node, graph, status, constants):
            self_confidence = 1
            return self_confidence

        initial_status = {
            'addiction': initial_addiction,
            'self_confidence': initial_self_confidence
        }

        def craving_model(node, graph, status, attributes, constants):
            current_val = status[node]['addiction']
            return min(current_val + 0.1, 1)

        def self_confidence_impact(node, graph, status, attributes, constants):
            return max(status[node]['self_confidence'] - 0.25, 0)

        # Network definition
        g = nx.erdos_renyi_graph(n=1000, p=0.1)

        # Model definition
        addiction_model = gc.ContinuousModel(g)
        addiction_model.add_status('addiction')
        addiction_model.add_status('self_confidence')

        # Compartments
        condition = cpm.NodeNumericalVariable('addiction', var_type=NumericalType.STATUS, value=1, op='<')

        # Rules
        addiction_model.add_rule('addiction', craving_model, condition)
        addiction_model.add_rule('self_confidence', self_confidence_impact, condition)

        # Configuration
        config = mc.Configuration()
        addiction_model.set_initial_status(initial_status, config)

        # Simulation
        iterations = addiction_model.iteration_bunch(50, node_status=True, tqdm=False)
        self.assertEqual(len(iterations), 50)

    def test_constants(self):
        g = nx.erdos_renyi_graph(n=1000, p=0.1)

        constants = {
                'constant_1': 0.1,
                'constant_2': 2.5
        }
        model = gc.ContinuousModel(g, constants=constants)

        self.assertEqual(constants, model.constants)

    def test_states(self):
        g = nx.erdos_renyi_graph(n=1000, p=0.1)
        model = gc.ContinuousModel(g)
        model.add_status('status1')
        model.add_status('status2')

        self.assertTrue('status1' in model.available_statuses.keys() and 'status2' in model.available_statuses.keys())

    def test_initial_values(self):
        def initial_status_1(node, graph, status, constants):
            return 1

        initial_status = {
            'status_1': initial_status_1,
            'status_2': 2
        }

        g = nx.erdos_renyi_graph(n=100, p=0.1)

        model = gc.ContinuousModel(g)

        model.add_status('status_1')
        model.add_status('status_2')

        config = mc.Configuration()
        model.set_initial_status(initial_status, config)

        self.assertEqual(model.initial_status[0]['status_1'], 1)
        self.assertEqual(model.initial_status[0]['status_2'], 2)

    def test_conditions(self):
        g = nx.erdos_renyi_graph(n=100, p=0.1)

        model = gc.ContinuousModel(g)

        model.add_status('status_1')
        model.add_status('status_2')

        # Compartments
        condition = cpm.NodeStochastic(1)

        # Update functions
        def update_1(node, graph, status, attributes, constants):
                return status[node]['status_2'] + 0.1

        def update_2(node, graph, status, attributes, constants):
                return status[node]['status_1'] + 0.5

        # Rules
        model.add_rule('status_1', update_1, condition)
        model.add_rule('status_2', update_2, condition)

        self.assertEqual(model.compartment_progressive, 2)
        self.assertEqual(model.compartment[0], ('status_1', update_1, condition, ['']))
        self.assertEqual(model.compartment[1], ('status_2', update_2, condition, ['']))

    def test_schemes(self):
        g = nx.erdos_renyi_graph(n=100, p=0.1)

        # Define schemes
        def sample_state_weighted(graph, status):
                probs = []
                status_1 = [stat['status_1'] for stat in list(status.values())]
                factor = 1.0/sum(status_1)
                for s in status_1:
                        probs.append(s * factor)
                return np.random.choice(graph.nodes, size=1, replace=False, p=probs)

        schemes = [
            {
                'name': 'random weighted agent',
                'function': sample_state_weighted,
                'lower': 100,
                'upper': 200
            }
        ]

        model = gc.ContinuousModel(g, iteration_schemes=schemes)

        model.add_status('status_1')
        model.add_status('status_2')

        # Compartments
        condition = cpm.NodeStochastic(1)

        # Update functions
        def update_1(node, graph, status, attributes, constants):
            return status[node]['status_2'] + 0.1

        def update_2(node, graph, status, attributes, constants):
            return status[node]['status_1'] + 0.5

        # Rules
        model.add_rule('status_1', update_1, condition, ['random weighted agent'])
        model.add_rule('status_2', update_2, condition)

        self.assertEqual(model.compartment_progressive, 2)
        self.assertEqual(model.compartment[0], ('status_1', update_1, condition, ['random weighted agent']))
        self.assertEqual(model.compartment[1], ('status_2', update_2, condition, ['']))
        self.assertTrue({
            'name': 'random weighted agent',
            'function': sample_state_weighted,
            'lower': 100,
            'upper': 200
        } in model.iteration_schemes)

    def test_save_file(self):
        def update(node, graph, status, attributes, constants):
            return 0

        initial_status = {
            'status': 0
        }

        # Network definition
        g = nx.erdos_renyi_graph(n=10, p=0.5)

        # Model definition
        path = './test_output/'
        output_path = path + 'file'
        model = gc.ContinuousModel(g, save_file=output_path)
        model.add_status('status')

        # Compartments
        condition = cpm.NodeStochastic(1)

        # Rules
        model.add_rule('status_1', update, condition)

        # Configuration
        config = mc.Configuration()
        model.set_initial_status(initial_status, config)

        # Simulation
        iterations = model.iteration_bunch(10, node_status=True, tqdm=False)
        self.assertEqual(len(iterations), 10)
        self.assertTrue(os.path.isfile(output_path + '.npy'))
        os.remove(output_path + '.npy')
        os.rmdir(path)
