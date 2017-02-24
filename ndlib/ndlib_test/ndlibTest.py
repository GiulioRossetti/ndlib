from __future__ import absolute_import
import unittest
import networkx as nx
import ndlib.VoterModel as vm
import ndlib.SznajdModel as sm
import ndlib.MajorityRuleModel as mrm
import ndlib.QVoterModel as qvm
import ndlib.SIModel as si
import ndlib.CognitiveOpDynModel as cm
import ndlib.KerteszThresholdModel as ks
import ndlib.SIRModel as sir
import ndlib.SISModel as sis
import ndlib.IndependentCascadesModel as ids
import ndlib.ThresholdModel as th
import ndlib.ProfileModel as pr
import ndlib.ProfileThresholdModel as pt

__author__ = 'Giulio Rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"


class NdlibTest(unittest.TestCase):
    def test_voter_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = vm.VoterModel(g)
        model.set_initial_status({'model': {'percentage_infected': 0.2}})
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_sznajd_model(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = sm.SznajdModel(g)
        model.set_initial_status({'model': {'percentage_infected': 0.2}})
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_majorityrule_model(self):
        g = nx.complete_graph(100)
        model = mrm.MajorityRuleModel(g, {'q': 3})
        model.set_initial_status({'model': {'percentage_infected': 0.6}})
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_qvoter_model(self):
        g = nx.complete_graph(100)
        model = qvm.QVoterModel(g, {'q': 5})
        model.set_initial_status({'model': {'percentage_infected': 0.6}})
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_cognitive_model(self):
        g = nx.complete_graph(100)
        model = cm.CognitiveOpDynModel(g, {'I': 0.15, 'B_range_min': 0,
                                           'B_range_max': 1, 'T_range_min': 0, 'T_range_max': 1,
                                           'R_fraction_negative': 1 / 3.0, 'R_fraction_neutral': 1 / 3.0,
                                           'R_fraction_positive': 1 / 3.0})
        model.set_initial_status()
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_si_model(self):
        g = nx.complete_graph(100)
        model = si.SIModel(g, {'beta': 0.5})
        model.set_initial_status({'model': {'percentage_infected': 0.1}})
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_sir_model(self):
        g = nx.complete_graph(100)
        model = sir.SIRModel(g, {'beta': 0.5, 'gamma': 0.2})
        model.set_initial_status({'model': {'percentage_infected': 0.1}})
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_sis_model(self):
        g = nx.complete_graph(100)
        model = sis.SISModel(g, {'beta': 0.5, 'lambda': 0.2})
        model.set_initial_status({'model': {'percentage_infected': 0.1}})
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_kertesz_model(self):
        g = nx.complete_graph(100)
        model = ks.KerteszThresholdModel(g, {'adopter_rate': 0.4, 'blocked': 0.1})
        threshold = 0.2
        threshold_list = (threshold, )
        for i in range(0, g.number_of_nodes()-1):
            threshold_list += threshold,
        model.set_initial_status({'model': {'percentage_infected': 0.1}, 'nodes': {'threshold': threshold_list}})
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_threshold_model(self):
        g = nx.complete_graph(100)
        model = th.ThresholdModel(g)
        threshold = 0.2
        threshold_list = (threshold, )
        for i in range(0, g.number_of_nodes()-1):
            threshold_list += threshold,
        model.set_initial_status({'model': {'percentage_infected': 0.1}, 'nodes': {'threshold': threshold_list}})
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_profile_threshold_model(self):
        g = nx.complete_graph(100)
        model = pt.ProfileThresholdModel(g)
        threshold = 0.2
        threshold_list = (threshold,)
        for i in range(0, g.number_of_nodes() - 1):
            threshold_list += threshold,

        profile = 0.1
        profile_threshold_list = (profile,)
        for i in range(0, g.number_of_nodes() - 1):
            profile_threshold_list += profile,

        model.set_initial_status({'model': {'percentage_infected': 0.1},
                                  'nodes': {'threshold': threshold_list, 'profile': profile_threshold_list}})
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_profile_model(self):
        g = nx.complete_graph(100)
        model = pr.ProfileModel(g)
        profile = 0.1
        profile_threshold_list = (profile,)
        for i in range(0, g.number_of_nodes() - 1):
            profile_threshold_list += profile,

        model.set_initial_status({'model': {'percentage_infected': 0.1},
                                  'nodes': {'profile': profile_threshold_list}})
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)

    def test_independent_cascade_model(self):
        g = nx.complete_graph(100)
        model = ids.IndependentCascadesModel(g)
        threshold = 0.2
        threshold_list = (threshold,)
        for i in range(0, g.number_of_nodes() - 1):
            threshold_list += threshold,

        model.set_initial_status({'model': {'percentage_infected': 0.1},
                                  'nodes': {'threshold': threshold_list}})
        iterations = model.iteration_bunch(10)
        self.assertEqual(len(iterations), 10)
