from __future__ import absolute_import

import unittest
import past.builtins
import dynetx as dn
import networkx as nx

import ndlib.models.ModelConfig as mc
import ndlib.models.dynamic as dyn

__author__ = "Giulio Rossetti"
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class DynTest(unittest.TestCase):
    def test_DynSI(self):
        dg = dn.DynGraph()

        for t in past.builtins.xrange(0, 3):
            g = nx.erdos_renyi_graph(200, 0.05)
            dg.add_interactions_from(g.edges(), t)

        model = dyn.DynSIModel(dg)
        config = mc.Configuration()
        config.add_model_parameter("beta", 0.1)
        config.add_model_parameter("fraction_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.execute_snapshots()
        self.assertEqual(len(iterations), 3)

        iterations = model.execute_iterations()
        trends = model.build_trends(iterations)
        self.assertEqual(
            len(trends[0]["trends"]["status_delta"][1]),
            len([x for x in dg.stream_interactions() if x[2] == "+"]),
        )

    def test_DynSIS(self):
        dg = dn.DynGraph()

        for t in past.builtins.xrange(0, 3):
            g = nx.erdos_renyi_graph(200, 0.05)
            dg.add_interactions_from(g.edges(), t)

        model = dyn.DynSISModel(dg)
        config = mc.Configuration()
        config.add_model_parameter("beta", 0.1)
        config.add_model_parameter("lambda", 0.1)
        config.add_model_parameter("fraction_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.execute_snapshots()
        self.assertEqual(len(iterations), 3)

        iterations = model.execute_iterations()
        trends = model.build_trends(iterations)
        self.assertEqual(
            len(trends[0]["trends"]["status_delta"][1]),
            len([x for x in dg.stream_interactions() if x[2] == "+"]),
        )

    def test_DynSIR(self):
        dg = dn.DynGraph()

        for t in past.builtins.xrange(0, 3):
            g = nx.erdos_renyi_graph(200, 0.05)
            dg.add_interactions_from(g.edges(), t)

        model = dyn.DynSIRModel(dg)
        config = mc.Configuration()
        config.add_model_parameter("beta", 0.1)
        config.add_model_parameter("gamma", 0.1)
        config.add_model_parameter("fraction_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.execute_snapshots()
        self.assertEqual(len(iterations), 3)

        iterations = model.execute_iterations()
        trends = model.build_trends(iterations)
        self.assertEqual(
            len(trends[0]["trends"]["status_delta"][1]),
            len([x for x in dg.stream_interactions() if x[2] == "+"]),
        )

    def test_DynProfile(self):
        dg = dn.DynGraph()

        for t in past.builtins.xrange(0, 3):
            g = nx.erdos_renyi_graph(200, 0.05)
            dg.add_interactions_from(g.edges(), t)

        model = dyn.DynProfileModel(dg)
        config = mc.Configuration()
        config.add_model_parameter("fraction_infected", 0.1)
        config.add_model_parameter("blocked", 0.1)
        config.add_model_parameter("adopter_rate", 0.001)

        profile = 0.1
        for i in g.nodes():
            config.add_node_configuration("profile", i, profile)

        model.set_initial_status(config)
        model.set_initial_status(config)
        iterations = model.execute_snapshots()
        self.assertEqual(len(iterations), 3)

    def test_DynProfileThreshold(self):
        dg = dn.DynGraph()

        for t in past.builtins.xrange(0, 3):
            g = nx.erdos_renyi_graph(200, 0.05)
            dg.add_interactions_from(g.edges(), t)

        model = dyn.DynProfileThresholdModel(dg)
        config = mc.Configuration()
        config.add_model_parameter("fraction_infected", 0.1)
        config.add_model_parameter("blocked", 0.1)
        config.add_model_parameter("adopter_rate", 0.001)

        threshold = 0.2
        profile = 0.1
        for i in g.nodes():
            config.add_node_configuration("threshold", i, threshold)
            config.add_node_configuration("profile", i, profile)

        model.set_initial_status(config)
        model.set_initial_status(config)
        iterations = model.execute_snapshots()
        self.assertEqual(len(iterations), 3)

    def test_DynKerteszThreshold(self):
        dg = dn.DynGraph()

        for t in past.builtins.xrange(0, 3):
            g = nx.erdos_renyi_graph(200, 0.05)
            dg.add_interactions_from(g.edges(), t)

        model = dyn.DynKerteszThresholdModel(dg)
        config = mc.Configuration()
        config.add_model_parameter("fraction_infected", 0.1)
        config.add_model_parameter("percentage_blocked", 0.1)
        config.add_model_parameter("adopter_rate", 0.001)

        threshold = 0.2
        for i in g.nodes():
            config.add_node_configuration("threshold", i, threshold)

        model.set_initial_status(config)
        model.set_initial_status(config)
        iterations = model.execute_snapshots()
        self.assertEqual(len(iterations), 3)
