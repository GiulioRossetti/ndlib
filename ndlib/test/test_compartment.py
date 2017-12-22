from __future__ import absolute_import

import unittest
import networkx as nx
import numpy as np
import ndlib.models.ModelConfig as mc
import ndlib.models.CompositeModel as gc
import ndlib.models.compartments.NodeStochastic as ns
import ndlib.models.compartments.NodeThreshold as nt
import ndlib.models.compartments.EdgeStochastic as es
import ndlib.models.compartments.ConditionalComposition as cif

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class NdlibCompartmentsTest(unittest.TestCase):

    def test_node_stochastic(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = gc.CompositeModel(g)

        model.add_status("Susceptible")
        model.add_status("Infected")
        model.add_status("Removed")

        c1 = ns.NodeStochastic(0.02, "Infected")
        c2 = ns.NodeStochastic(0.01)
        c3 = ns.NodeStochastic(0.5)

        model.add_rule("Susceptible", "Infected", c1)
        model.add_rule("Infected", "Removed", c2)
        model.add_rule("Infected", "Susceptible", c3)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(100)
        self.assertEqual(len(iterations), 100)

    def test_node_threshold(self):

        # Fixed Threshold
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = gc.CompositeModel(g)

        model.add_status("Susceptible")
        model.add_status("Infected")

        c1 = nt.NodeThreshold(0.1, triggering_status="Infected")
        model.add_rule("Susceptible", "Infected", c1)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        # Ad-hoc Threshold
        model = gc.CompositeModel(g)

        model.add_status("Susceptible")
        model.add_status("Infected")

        c1 = nt.NodeThreshold(triggering_status="Infected")
        model.add_rule("Susceptible", "Infected", c1)

        config = mc.Configuration()

        for i in g.nodes():
            config.add_node_configuration("threshold", i, np.random.random_sample())

        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_edge_stochastic(self):

        # Fixed Threshold
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = gc.CompositeModel(g)

        model.add_status("Susceptible")
        model.add_status("Infected")

        c1 = es.EdgeStochastic(0.1, triggering_status="Infected")
        model.add_rule("Susceptible", "Infected", c1)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        # Ad-hoc Threshold
        model = gc.CompositeModel(g)

        model.add_status("Susceptible")
        model.add_status("Infected")

        c1 = es.EdgeStochastic(triggering_status="Infected")
        model.add_rule("Susceptible", "Infected", c1)

        config = mc.Configuration()

        for e in g.edges():
            config.add_edge_configuration("threshold", e, np.random.random_sample())

        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        # Predefined threshold 1/N

        model = gc.CompositeModel(g)

        model.add_status("Susceptible")
        model.add_status("Infected")

        c1 = es.EdgeStochastic(triggering_status="Infected")
        model.add_rule("Susceptible", "Infected", c1)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_node_stochastic_composed(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = gc.CompositeModel(g)

        model.add_status("Susceptible")
        model.add_status("Infected")
        model.add_status("Removed")

        # cascading composition
        c3 = ns.NodeStochastic(0.2)
        c2 = ns.NodeStochastic(0.4, composed=c3)
        c1 = ns.NodeStochastic(0.5, "Infected", composed=c2)

        model.add_rule("Susceptible", "Infected", c1)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(100)
        self.assertEqual(len(iterations), 100)

    def test_conditional_composition(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = gc.CompositeModel(g)

        model.add_status("Susceptible")
        model.add_status("Infected")
        model.add_status("Removed")

        # conditional composition
        c1 = ns.NodeStochastic(0.5)
        c2 = ns.NodeStochastic(0.2)
        c3 = ns.NodeStochastic(0.1)

        cc = cif.ConditionalComposition(c1, c2, c3)

        model.add_rule("Susceptible", "Infected", cc)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(100)
        self.assertEqual(len(iterations), 100)