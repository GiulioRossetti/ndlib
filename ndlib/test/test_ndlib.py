from __future__ import absolute_import

import unittest

import future.utils
import networkx as nx

import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics as epd
import ndlib.models.opinions as opn
import ndlib.utils as ut

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class NdlibTest(unittest.TestCase):
    
    def test_algorithmic_bias_model(self):
        g = nx.complete_graph(100)
        model = opn.AlgorithmicBiasModel(g)
        config = mc.Configuration()
        config.add_model_parameter("epsilon", 0.32)
        config.add_model_parameter("gamma", 1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)
    
    def test_voter_model(self):
        g = nx.complete_graph(100)
        model = opn.VoterModel(g)
        config = mc.Configuration()
        config.add_model_parameter("percentage_infected", 0.2)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_sznajd_model(self):
        g = nx.complete_graph(100)
        model = opn.SznajdModel(g)
        config = mc.Configuration()
        config.add_model_parameter("percentage_infected", 0.2)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

        g = nx.complete_graph(100)
        g = g.to_directed()
        model = opn.SznajdModel(g)
        config = mc.Configuration()
        config.add_model_parameter("percentage_infected", 0.2)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_majorityrule_model(self):
        g = nx.complete_graph(100)
        model = opn.MajorityRuleModel(g)
        config = mc.Configuration()
        config.add_model_parameter("q", 3)
        config.add_model_parameter("percentage_infected", 0.2)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_qvoter_model(self):
        g = nx.complete_graph(100)
        model = opn.QVoterModel(g)
        config = mc.Configuration()
        config.add_model_parameter("q", 5)
        config.add_model_parameter("percentage_infected", 0.6)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_cognitive_model(self):
        g = nx.complete_graph(100)
        model = opn.CognitiveOpDynModel(g)
        config = mc.Configuration()
        config.add_model_parameter("I", 0.15)
        config.add_model_parameter("B_range_min", 0)
        config.add_model_parameter("B_range_max", 1)
        config.add_model_parameter("T_range_min", 0)
        config.add_model_parameter("T_range_max", 1)
        config.add_model_parameter("R_fraction_negative", 1.0 / 3)
        config.add_model_parameter("R_fraction_neutral", 1.0 / 3)
        config.add_model_parameter("R_fraction_positive", 1.0 / 3)
        model.set_initial_status(config)

        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_si_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.SIModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.5)
        config.add_model_parameter("percentage_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_sir_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.SIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.5)
        config.add_model_parameter('gamma', 0.2)
        config.add_model_parameter("percentage_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_seir_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.SEIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.5)
        config.add_model_parameter('gamma', 0.2)
        config.add_model_parameter('alpha', 0.05)
        config.add_model_parameter("percentage_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        g = g.to_directed()
        model = epd.SEIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.5)
        config.add_model_parameter('gamma', 0.8)
        config.add_model_parameter('alpha', 0.5)
        config.add_model_parameter("percentage_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_swir_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.SWIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('kappa', 0.5)
        config.add_model_parameter('mu', 0.2)
        config.add_model_parameter('nu', 0.05)
        config.add_model_parameter("percentage_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_seis_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.SEISModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.5)
        config.add_model_parameter('lambda', 0.2)
        config.add_model_parameter('alpha', 0.05)
        config.add_model_parameter("percentage_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        g = g.to_directed()
        model = epd.SEISModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.5)
        config.add_model_parameter('lambda', 0.8)
        config.add_model_parameter('alpha', 0.5)
        config.add_model_parameter("percentage_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_sis_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.SISModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.5)
        config.add_model_parameter('lambda', 0.2)
        config.add_model_parameter("percentage_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_kertesz_model(self):
        g = nx.complete_graph(100)
        model = epd.KerteszThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('adopter_rate', 0.4)
        config.add_model_parameter('percentage_blocked', 0.1)
        config.add_model_parameter('percentage_infected', 0.1)

        threshold = 0.2
        for i in g.nodes():
            config.add_node_configuration("threshold", i, threshold)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_multiple_si_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.SIModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.01)
        config.add_model_parameter("percentage_infected", 0.1)
        model.set_initial_status(config)
        executions = ut.multi_runs(model, execution_number=10, iteration_number=50)
        self.assertEqual(len(executions), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_threshold_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.ThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        threshold = 0.2
        for i in g.nodes():
            config.add_node_configuration("threshold", i, threshold)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_generalisedthreshold_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.GeneralisedThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        config.add_model_parameter('tau', 5)
        config.add_model_parameter('mu', 5)

        threshold = 0.2
        for i in g.nodes():
            config.add_node_configuration("threshold", i, threshold)
        model.set_initial_status(config)

        iterations = model.iteration_bunch(50)
        self.assertEqual(len(iterations), 50)
        iterations = model.iteration_bunch(50, node_status=False)
        self.assertEqual(len(iterations), 50)

    def test_profile_threshold_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.ProfileThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        threshold = 0.2
        profile = 0.1
        for i in g.nodes():
            config.add_node_configuration("threshold", i, threshold)
            config.add_node_configuration("profile", i, profile)

        model.set_initial_status(config)

        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        model = epd.ProfileThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        config.add_model_parameter("blocked", 0.1)
        config.add_model_parameter("adopter_rate", 0.001)

        threshold = 0.2
        profile = 0.1
        for i in g.nodes():
            config.add_node_configuration("threshold", i, threshold)
            config.add_node_configuration("profile", i, profile)

        model.set_initial_status(config)

        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_profile_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.ProfileModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        profile = 0.1
        for i in g.nodes():
            config.add_node_configuration("profile", i, profile)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        model = epd.ProfileModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        config.add_model_parameter("blocked", 0.1)
        config.add_model_parameter("adopter_rate", 0.001)

        profile = 0.1
        for i in g.nodes():
            config.add_node_configuration("profile", i, profile)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_independent_cascade_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.IndependentCascadesModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        threshold = 0.1
        for e in g.edges():
            config.add_edge_configuration("threshold", e, threshold)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
        iterations = model.iteration_bunch(10, node_status=False)
        self.assertEqual(len(iterations), 10)

    def test_kertesz_model_predefined_blocked(self):
        g = nx.complete_graph(100)
        model = epd.KerteszThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('adopter_rate', 0.4)
        predefined_blocked = [0, 1, 2, 3, 4, 5]
        config.add_model_initial_configuration("Blocked", predefined_blocked)
        config.add_model_parameter('percentage_infected', 0.1)

        threshold = 0.2
        for i in g.nodes():
            config.add_node_configuration("threshold", i, threshold)

        model.set_initial_status(config)
        iteration = model.iteration()
        blocked = [x for x, v in future.utils.iteritems(iteration['status']) if v == -1]
        self.assertEqual(blocked, predefined_blocked)

    def test_initial_infected(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.SISModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.5)
        config.add_model_parameter('lambda', 0.2)
        predefined_infected = [0, 1, 2, 3, 4, 5]
        config.add_model_initial_configuration("Infected", predefined_infected)
        model.set_initial_status(config)
        inft = [k for k, v in future.utils.iteritems(model.status) if v == 1]
        self.assertAlmostEqual(inft, predefined_infected)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_optional_parameters(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.ThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        config.add_node_set_configuration("test", {n: 1 for n in g.nodes()})
        config.add_edge_set_configuration("etest", {e: 1 for e in g.edges()})

        self.assertEqual(len(iterations), 10)

        model = epd.KerteszThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('adopter_rate', 0.4)
        predefined_blocked = [0, 1, 2, 3, 4, 5]
        config.add_model_initial_configuration("Blocked", predefined_blocked)
        config.add_model_parameter('percentage_infected', 0.1)
        model.set_initial_status(config)
        iteration = model.iteration()
        blocked = [x for x, v in future.utils.iteritems(iteration["status"]) if v == -1]
        self.assertEqual(blocked, predefined_blocked)

        model = epd.IndependentCascadesModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        model = epd.ProfileModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        model = epd.ProfileThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        model = epd.ThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        model = epd.KerteszThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('adopter_rate', 0.4)
        config.add_model_parameter('percentage_blocked', 0.1)
        config.add_model_parameter('percentage_infected', 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_config(self):
        g = nx.erdos_renyi_graph(99, 0.1)
        model = epd.ThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        config.add_model_initial_configuration("Infected", [1, 2, 3])
        config.add_node_set_configuration("partial", {1: 1, 2: 2})
        try:
            model.set_initial_status(config)
        except:
            pass

        config.add_edge_set_configuration("partial", {e: 1 for e in list(g.edges)[:10]})
        try:
            model.set_initial_status(config)
        except:
            pass
        config.add_node_set_configuration("partial", {n: 1 for n in g.nodes})
        config.add_edge_set_configuration("partial", {e: 1 for e in g.edges})
        model.set_initial_status(config)

        g = nx.complete_graph(100)
        model = opn.MajorityRuleModel(g)
        config = mc.Configuration()
        config.add_model_parameter("percentage_infected", 0.2)
        try:
            model.set_initial_status(config)
        except:
            pass

        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.IndependentCascadesModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        try:
            model.set_initial_status(config)
        except:
            pass

        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.ThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        try:
            model.set_initial_status(config)
        except:
            pass
