from __future__ import absolute_import

import unittest
import dynetx as dn
import networkx as nx
import numpy as np
import past.builtins
import ndlib.models.ModelConfig as mc
import ndlib.models.DynamicCompostiteModel as gc
import ndlib.models.compartments.NodeStochastic as ns
import ndlib.models.compartments.NodeThreshold as nt
import ndlib.models.compartments.EdgeStochastic as es

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class NdlibDynCompartmentsTest(unittest.TestCase):

    def test_dyn_node_stochastic(self):

        dg = dn.DynGraph()

        for t in past.builtins.xrange(0, 3):
            g = nx.erdos_renyi_graph(200, 0.05)
            dg.add_interactions_from(g.edges(), t)

        model = gc.DynamicCompositeModel(dg)

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
        iterations = model.execute_snapshots()
        self.assertEqual(len(iterations), 3)

        iterations = model.execute_iterations()
        trends = model.build_trends(iterations)
        self.assertEqual(len(trends[0]['trends']['status_delta'][1]),
                         len([x for x in dg.stream_interactions() if x[2] == "+"]))

    def test_dyn_node_threshold(self):

        # Fixed Threshold
        dg = dn.DynGraph()

        for t in past.builtins.xrange(0, 3):
            g = nx.erdos_renyi_graph(200, 0.05)
            dg.add_interactions_from(g.edges(), t)

        model = gc.DynamicCompositeModel(dg)

        model.add_status("Susceptible")
        model.add_status("Infected")

        c1 = nt.NodeThreshold(0.1, triggering_status="Infected")
        model.add_rule("Susceptible", "Infected", c1)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.execute_snapshots()
        self.assertEqual(len(iterations), 3)

        iterations = model.execute_iterations()
        trends = model.build_trends(iterations)
        self.assertEqual(len(trends[0]['trends']['status_delta'][1]),
                         len([x for x in dg.stream_interactions() if x[2] == "+"]))

        # Ad-hoc Threshold
        model = gc.DynamicCompositeModel(dg)

        model.add_status("Susceptible")
        model.add_status("Infected")

        c1 = nt.NodeThreshold(triggering_status="Infected")
        model.add_rule("Susceptible", "Infected", c1)

        config = mc.Configuration()

        for i in g.nodes():
            config.add_node_configuration("threshold", i, np.random.random_sample())

        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.execute_snapshots()
        self.assertEqual(len(iterations), 3)

        iterations = model.execute_iterations()
        trends = model.build_trends(iterations)
        self.assertEqual(len(trends[0]['trends']['status_delta'][1]),
                         len([x for x in dg.stream_interactions() if x[2] == "+"]))

    def test_dyn_edge_stochastic(self):

        # Fixed Threshold
        dg = dn.DynGraph()

        for t in past.builtins.xrange(0, 3):
            g = nx.erdos_renyi_graph(200, 0.05)
            dg.add_interactions_from(g.edges(), t)

        model = gc.DynamicCompositeModel(dg)

        model.add_status("Susceptible")
        model.add_status("Infected")

        c1 = es.EdgeStochastic(0.1, triggering_status="Infected")
        model.add_rule("Susceptible", "Infected", c1)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.execute_snapshots()
        self.assertEqual(len(iterations), 3)

        iterations = model.execute_iterations()
        trends = model.build_trends(iterations)
        self.assertEqual(len(trends[0]['trends']['status_delta'][1]),
                         len([x for x in dg.stream_interactions() if x[2] == "+"]))

        # Ad-hoc Threshold
        model = gc.DynamicCompositeModel(dg)

        model.add_status("Susceptible")
        model.add_status("Infected")

        c1 = es.EdgeStochastic(triggering_status="Infected")
        model.add_rule("Susceptible", "Infected", c1)

        config = mc.Configuration()

        for e in g.edges():
            config.add_edge_configuration("threshold", e, np.random.random_sample())

        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.execute_snapshots()
        self.assertEqual(len(iterations), 3)

        iterations = model.execute_iterations()
        trends = model.build_trends(iterations)
        self.assertEqual(len(trends[0]['trends']['status_delta'][1]),
                         len([x for x in dg.stream_interactions() if x[2] == "+"]))

        # Predefined threshold 1/N
        model = gc.DynamicCompositeModel(dg)

        model.add_status("Susceptible")
        model.add_status("Infected")

        c1 = es.EdgeStochastic(triggering_status="Infected")
        model.add_rule("Susceptible", "Infected", c1)

        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        model.set_initial_status(config)
        iterations = model.execute_snapshots()
        self.assertEqual(len(iterations), 3)

        iterations = model.execute_iterations()
        trends = model.build_trends(iterations)
        self.assertEqual(len(trends[0]['trends']['status_delta'][1]),
                         len([x for x in dg.stream_interactions() if x[2] == "+"]))