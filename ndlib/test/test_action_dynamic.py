from __future__ import absolute_import

import unittest
import networkx as nx
import numpy as np
import ndlib.models.ModelConfig as mc
import ndlib.models.CompositeModel as gc
import ndlib.models.compartments.NodeStochastic as ns
import ndlib.models.compartments.NodeThreshold as nt
import ndlib.models.compartments.NodeCategoricalAttribute as na
import ndlib.models.compartments.NodeNumericalAttribute as nm
import ndlib.models.compartments.EdgeStochastic as es
import ndlib.models.compartments.EdgeCategoricalAttribute as ea
import ndlib.models.compartments.EdgeNumericalAttribute as en
import ndlib.models.compartments.ConditionalComposition as cif
import ndlib.models.compartments.CountDown as cw

import ndlib.models.actions.AddNode as ad
import ndlib.models.actions.RemoveNode as rn
import ndlib.models.actions.SwapEdges as ew

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class NdlibActionDynamicTest(unittest.TestCase):

    def test_compartment_add_node(self):

        g = nx.karate_club_graph()
        attr = {n: {"even": int(n % 2)} for n in g.nodes()}
        nx.set_node_attributes(g, attr)

        model = gc.CompositeModel(g)
        model.add_status("Susceptible")
        model.add_status("Infected")

        a1 = ad.AddNode(probability=1, initial_status="Susceptible", copy_attributes=True)
        c1 = ns.NodeStochastic(1)

        model.add_rule("Susceptible", "Susceptible", c1)
        model.add_action(a1)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(6)
        nodes = [sum(n['node_count'].values()) for n in iterations]
        self.assertEqual(nodes, [35, 36, 37, 38, 39, 40])

    def test_compartment_swap_edge(self):

        g = nx.karate_club_graph()
        attr = {(u, v): {"even": int((u + v) % 10)} for (u, v) in g.edges()}
        nx.set_edge_attributes(g, attr)

        model = gc.CompositeModel(g)
        model.add_status("Susceptible")
        model.add_status("Infected")

        a1 = ew.SwapEdges(probability=1, number_of_swaps=1, copy_attributes=True, initial_status="Susceptible")
        c1 = ns.NodeStochastic(0.5)

        model.add_rule("Susceptible", "Susceptible", c1)
        model.add_action(a1)

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

        a1 = rn.RemoveNode(probability=1)
        c1 = ns.NodeStochastic(0.5)

        model.add_rule("Susceptible", "Susceptible", c1)
        model.add_action(a1)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(6)
        nodes = [sum(n['node_count'].values()) for n in iterations]
        self.assertEqual(nodes, [33, 32, 31, 30, 29, 28])