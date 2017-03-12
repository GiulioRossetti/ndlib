from __future__ import absolute_import
import unittest
import networkx as nx
import ndlib.models.ModelConfig as mc
import ndlib.models.opinions.VoterModel as vm
import ndlib.models.opinions.SznajdModel as sm
import ndlib.models.opinions.MajorityRuleModel as mrm
import ndlib.models.opinions.QVoterModel as qvm
import ndlib.models.opinions.CognitiveOpDynModel as cm
import ndlib.models.epidemics.SIModel as si
import ndlib.models.epidemics.KerteszThresholdModel as ks
import ndlib.models.epidemics.SIRModel as sir
import ndlib.models.epidemics.SISModel as sis
import ndlib.models.epidemics.IndependentCascadesModel as ids
import ndlib.models.epidemics.ThresholdModel as th
import ndlib.models.epidemics.ProfileModel as pr
import ndlib.models.epidemics.ProfileThresholdModel as pt

__author__ = 'Giulio Rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"


class NdlibTest(unittest.TestCase):
    def test_voter_model(self):
        g = nx.complete_graph(100)
        model = vm.VoterModel(g)
        config = mc.Configuration()
        config.add_model_parameter("percentage_infected", 0.2)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_sznajd_model(self):
        g = nx.complete_graph(100)
        model = sm.SznajdModel(g)
        config = mc.Configuration()
        config.add_model_parameter("percentage_infected", 0.2)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_majorityrule_model(self):
        g = nx.complete_graph(100)
        model = mrm.MajorityRuleModel(g)
        config = mc.Configuration()
        config.add_model_parameter("q", 3)
        config.add_model_parameter("percentage_infected", 0.2)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_qvoter_model(self):
        g = nx.complete_graph(100)
        model = qvm.QVoterModel(g)
        config = mc.Configuration()
        config.add_model_parameter("q", 5)
        config.add_model_parameter("percentage_infected", 0.6)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_cognitive_model(self):
        g = nx.complete_graph(100)
        model = cm.CognitiveOpDynModel(g)
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

    def test_si_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = si.SIModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.5)
        config.add_model_parameter("percentage_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_sir_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = sir.SIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.5)
        config.add_model_parameter('gamma', 0.2)
        config.add_model_parameter("percentage_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_sis_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = sis.SISModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.5)
        config.add_model_parameter('lambda', 0.2)
        config.add_model_parameter("percentage_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_kertesz_model(self):
        g = nx.complete_graph(100)
        model = ks.KerteszThresholdModel(g)
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

    def test_threshold_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = th.ThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        threshold = 0.2
        for i in g.nodes():
            config.add_node_configuration("threshold", i, threshold)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_profile_threshold_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = pt.ProfileThresholdModel(g)
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

    def test_profile_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = pr.ProfileModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)

        profile = 0.1
        for i in g.nodes():
            config.add_node_configuration("profile", i, profile)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_independent_cascade_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = ids.IndependentCascadesModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        threshold = 0.1
        for e in g.edges():
            config.add_edge_configuration("threshold", e, threshold)

        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_kertesz_model_predefined_blocked(self):
        g = nx.complete_graph(100)
        model = ks.KerteszThresholdModel(g)
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
        blocked = [x for x, v in iteration[1].iteritems() if v == -1]
        self.assertEqual(blocked, predefined_blocked)

    def test_initial_infected(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = sis.SISModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.5)
        config.add_model_parameter('lambda', 0.2)
        predefined_infected = [0, 1, 2, 3, 4, 5]
        config.add_model_initial_configuration("Infected", predefined_infected)
        model.set_initial_status(config)
        inft = [k for k, v in model.status.iteritems() if v == 1]
        self.assertAlmostEqual(inft, predefined_infected)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_optional_parameters(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = th.ThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        model = ks.KerteszThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('adopter_rate', 0.4)
        predefined_blocked = [0, 1, 2, 3, 4, 5]
        config.add_model_initial_configuration("Blocked", predefined_blocked)
        config.add_model_parameter('percentage_infected', 0.1)
        model.set_initial_status(config)
        iteration = model.iteration()
        blocked = [x for x, v in iteration[1].iteritems() if v == -1]
        self.assertEqual(blocked, predefined_blocked)

        model = ids.IndependentCascadesModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        model = pr.ProfileModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        model = pt.ProfileThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        model = th.ThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('percentage_infected', 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

        model = ks.KerteszThresholdModel(g)
        config = mc.Configuration()
        config.add_model_parameter('adopter_rate', 0.4)
        config.add_model_parameter('percentage_blocked', 0.1)
        config.add_model_parameter('percentage_infected', 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
