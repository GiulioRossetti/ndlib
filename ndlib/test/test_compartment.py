from __future__ import absolute_import

import unittest
import networkx as nx
import numpy as np
import ndlib.models.ModelConfig as mc
import ndlib.models.CompositeModel as gc
import ndlib.models.compartments as cpm

import ndlib.models.actions as act

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

        c1 = cpm.NodeStochastic(0.02, "Infected")
        c2 = cpm.NodeStochastic(0.01)
        c3 = cpm.NodeStochastic(0.5)

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

        c1 = cpm.NodeThreshold(0.1, triggering_status="Infected")
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

        c1 = cpm.NodeThreshold(triggering_status="Infected")
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

        c1 = cpm.EdgeStochastic(0.1, triggering_status="Infected")
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

        c1 = cpm.EdgeStochastic(triggering_status="Infected")
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

        c1 = cpm.EdgeStochastic(triggering_status="Infected")
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
        c3 = cpm.NodeStochastic(0.2)
        c2 = cpm.NodeStochastic(0.4, composed=c3)
        c1 = cpm.NodeStochastic(0.5, "Infected", composed=c2)

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
        c1 = cpm.NodeStochastic(0.5)
        c2 = cpm.NodeStochastic(0.2)
        c3 = cpm.NodeStochastic(0.1)

        cc = cpm.ConditionalComposition(c1, c2, c3)

        model.add_rule("Susceptible", "Infected", cc)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(100)
        self.assertEqual(len(iterations), 100)

    def test_node_attribute(self):

        g = nx.karate_club_graph()
        attr = {n: {"even": int(n % 2)} for n in g.nodes()}
        nx.set_node_attributes(g, attr)

        model = gc.CompositeModel(g)
        model.add_status("Susceptible")
        model.add_status("Infected")

        c = cpm.NodeCategoricalAttribute("even", "0", probability=0.6)
        model.add_rule("Susceptible", "Infected", c)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_edge_attribute(self):

        g = nx.karate_club_graph()
        attr = {(u, v): {"even": int((u+v) % 2)} for (u, v) in g.edges()}
        nx.set_edge_attributes(g, attr)

        model = gc.CompositeModel(g)
        model.add_status("Susceptible")
        model.add_status("Infected")

        c = cpm.EdgeCategoricalAttribute("even", "0", probability=0.6)
        model.add_rule("Susceptible", "Infected", c)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_countwodn(self):

        g = nx.karate_club_graph()

        model = gc.CompositeModel(g)
        model.add_status("Susceptible")
        model.add_status("Infected")

        c = cpm.CountDown(name="time", iterations=4)
        model.add_rule("Susceptible", "Infected", c)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(100)
        self.assertEqual(len(iterations), 100)

    def test_node_num_attribute(self):

        g = nx.karate_club_graph()
        attr = {n: {"even": int(n % 10)} for n in g.nodes()}
        nx.set_node_attributes(g, attr)

        model = gc.CompositeModel(g)
        model.add_status("Susceptible")
        model.add_status("Infected")

        c = cpm.NodeNumericalAttribute("even", value=0, op="==", probability=1)
        model.add_rule("Susceptible", "Infected", c)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        model = gc.CompositeModel(g)
        model.add_status("Susceptible")
        model.add_status("Infected")

        c = cpm.NodeNumericalAttribute("even", value=[3, 5], op="IN", probability=1)
        model.add_rule("Susceptible", "Infected", c)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_edge_num_attribute(self):

        g = nx.karate_club_graph()
        attr = {(u, v): {"even": int((u+v) % 10)} for (u, v) in g.edges()}
        nx.set_edge_attributes(g, attr)

        model = gc.CompositeModel(g)
        model.add_status("Susceptible")
        model.add_status("Infected")

        c = cpm.EdgeNumericalAttribute("even", value=0, op="==", probability=1)
        model.add_rule("Susceptible", "Infected", c)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        model = gc.CompositeModel(g)
        model.add_status("Susceptible")
        model.add_status("Infected")

        c = cpm.EdgeNumericalAttribute("even", value=[3, 10], op="IN", probability=1)
        model.add_rule("Susceptible", "Infected", c)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_compartment_add_node(self):

        g = nx.karate_club_graph()
        attr = {n: {"even": int(n % 2)} for n in g.nodes()}
        nx.set_node_attributes(g, attr)

        model = gc.CompositeModel(g)
        model.add_status("Susceptible")
        model.add_status("Infected")

        c2 = act.AddNode(probability=1, initial_status="Susceptible", copy_attributes=True)
        c1 = cpm.NodeStochastic(1, composed=c2)

        model.add_rule("Susceptible", "Susceptible", c1)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(6)
        nodes = [sum(n['node_count'].values()) for n in iterations]

        self.assertEqual(nodes, [34, 67, 133, 265, 529, 1057])

    def test_compartment_swap_edge(self):

        g = nx.karate_club_graph()
        attr = {(u, v): {"even": int((u + v) % 10)} for (u, v) in g.edges()}
        nx.set_edge_attributes(g, attr)

        model = gc.CompositeModel(g)
        model.add_status("Susceptible")
        model.add_status("Infected")

        c2 = act.SwapEdges(probability=1, number_of_swaps=1, copy_attributes=True, initial_status="Susceptible")
        c1 = cpm.NodeStochastic(1, composed=c2)

        model.add_rule("Susceptible", "Susceptible", c1)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(6)
        self.assertEqual(len(iterations), 6)

    def test_compartment_remove_node(self):

        g = nx.karate_club_graph()

        model = gc.CompositeModel(g)
        model.add_status("Susceptible")
        model.add_status("Infected")

        c2 = act.RemoveNode(probability=1)
        c1 = cpm.NodeStochastic(1, composed=c2)

        model.add_rule("Susceptible", "Susceptible", c1)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(6)
        nodes = [sum(n['node_count'].values()) for n in iterations]
        self.assertEqual(nodes, [34, 1, 1, 1, 1, 1])