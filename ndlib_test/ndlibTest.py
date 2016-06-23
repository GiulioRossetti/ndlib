import unittest
import networkx as nx
import sys
sys.path.append("..")
import ndlib.VoterModel as vm
import ndlib.SznajdModel as sm
import ndlib.MajorityRuleModel as mrm

__author__ = 'rossetti'
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
