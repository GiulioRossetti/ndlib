from __future__ import absolute_import
import unittest
import ndlib.parser.ExperimentParser as ep
import networkx as nx
import os

__author__ = "Giulio Rossetti"
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class NdlibParserTest(unittest.TestCase):
    def test_node_stochastic(self):
        query = (
            "CREATE_NETWORK g1\n"
            "TYPE erdos_renyi_graph\n"
            "PARAM n 300\n"
            "PARAM p 0.1\n"
            "\n"
            "MODEL model1\n"
            "\n"
            "STATUS Susceptible\n"
            "\n"
            "STATUS Infected\n"
            "\n"
            "STATUS Removed\n"
            "\n"
            "COMPARTMENT c1\n"
            "TYPE NodeStochastic\n"
            "PARAM rate 0.1\n"
            "TRIGGER Infected\n"
            "\n"
            "COMPARTMENT c2\n"
            "TYPE NodeStochastic\n"
            "PARAM rate 0.1\n"
            "COMPOSE c1\n"
            "TRIGGER Infected\n"
            "\n"
            "COMPARTMENT c3\n"
            "TYPE NodeStochastic\n"
            "PARAM rate 0.1\n"
            "\n"
            "RULE\n"
            "FROM Susceptible\n"
            "TO Infected\n"
            "USING c2\n"
            "\n"
            "RULE\n"
            "FROM Infected\n"
            "TO Removed\n"
            "USING c3\n"
            "\n"
            "INITIALIZE\n"
            "SET Infected 0.1\n"
            "\n"
            "EXECUTE model1 ON g1 FOR 100"
        )

        parser = ep.ExperimentParser()
        parser.set_query(query)
        parser.parse()
        iterations = parser.execute_query()
        self.assertIn("trends", iterations[0])

    def test_ifcompose(self):
        query = (
            "CREATE_NETWORK g1\n"
            "TYPE erdos_renyi_graph\n"
            "PARAM n 300\n"
            "PARAM p 0.1\n"
            "\n"
            "MODEL model1\n"
            "\n"
            "STATUS Susceptible\n"
            "\n"
            "STATUS Infected\n"
            "\n"
            "STATUS Removed\n"
            "\n"
            "COMPARTMENT c1\n"
            "TYPE NodeStochastic\n"
            "PARAM rate 0.1\n"
            "TRIGGER Infected\n"
            "\n"
            "COMPARTMENT c2\n"
            "TYPE NodeStochastic\n"
            "PARAM rate 0.1\n"
            "TRIGGER Infected\n"
            "\n"
            "COMPARTMENT c3\n"
            "TYPE NodeStochastic\n"
            "PARAM rate 0.1\n"
            "\n"
            "IF c1 THEN c2 ELSE c3 AS r1\n"
            "\n"
            "RULE\n"
            "FROM Infected\n"
            "TO Removed\n"
            "USING r1\n"
            "\n"
            "INITIALIZE\n"
            "SET Infected 0.1\n"
            "\n"
            "EXECUTE model1 ON g1 FOR 100"
        )

        parser = ep.ExperimentParser()
        parser.set_query(query)
        parser.parse()
        iterations = parser.execute_query()
        self.assertIn("trends", iterations[0])

    def test_net_load(self):
        base = os.path.dirname(os.path.abspath(__file__))

        g = nx.karate_club_graph()
        fname = "%s/edge.txt" % base
        nx.write_edgelist(g, fname)

        query = (
            "LOAD_NETWORK g1 FROM %s\n"
            "\n"
            "MODEL model1\n"
            "\n"
            "STATUS Susceptible\n"
            "\n"
            "STATUS Infected\n"
            "\n"
            "STATUS Removed\n"
            "\n"
            "COMPARTMENT c1\n"
            "TYPE NodeStochastic\n"
            "PARAM rate 0.1\n"
            "TRIGGER Infected\n"
            "\n"
            "COMPARTMENT c2\n"
            "TYPE NodeStochastic\n"
            "PARAM rate 0.1\n"
            "COMPOSE c1\n"
            "TRIGGER Infected\n"
            "\n"
            "COMPARTMENT c3\n"
            "TYPE NodeStochastic\n"
            "PARAM rate 0.1\n"
            "\n"
            "RULE\n"
            "FROM Susceptible\n"
            "TO Infected\n"
            "USING c2\n"
            "\n"
            "RULE\n"
            "FROM Infected\n"
            "TO Removed\n"
            "USING c3\n"
            "\n"
            "INITIALIZE\n"
            "SET Infected 0.1\n"
            "\n"
            "EXECUTE model1 ON g1 FOR 10" % fname
        )

        parser = ep.ExperimentParser()
        parser.set_query(query)
        parser.parse()
        iterations = parser.execute_query()

        try:
            os.remove("%s/edge.txt" % base)
        except OSError:
            pass

        self.assertIn("trends", iterations[0])

    def test_node_countdown(self):
        query = (
            "CREATE_NETWORK g1\n"
            "TYPE erdos_renyi_graph\n"
            "PARAM n 300\n"
            "PARAM p 0.1\n"
            "\n"
            "MODEL model1\n"
            "\n"
            "STATUS Susceptible\n"
            "\n"
            "STATUS Infected\n"
            "\n"
            "STATUS Removed\n"
            "STATUS Wait\n"
            "\n"
            "COMPARTMENT c1\n"
            "TYPE NodeStochastic\n"
            "PARAM rate 0.1\n"
            "TRIGGER Infected\n"
            "\n"
            "COMPARTMENT c2\n"
            "TYPE CountDown\n"
            "PARAM iterations 5\n"
            "PARAM name time\n"
            "\n"
            "RULE\n"
            "FROM Susceptible\n"
            "TO Infected\n"
            "USING c1\n"
            "\n"
            "RULE\n"
            "FROM Infected\n"
            "TO Removed\n"
            "USING c2\n"
            "\n"
            "INITIALIZE\n"
            "SET Infected 0.1\n"
            "\n"
            "EXECUTE model1 ON g1 FOR 100"
        )

        parser = ep.ExperimentParser()
        parser.set_query(query)
        parser.parse()
        iterations = parser.execute_query()
        self.assertIn("trends", iterations[0])

    def test_continuous_opinion_builder_ndql(self):
        query = (
            "MODEL OpinionMixModel\n"
            "TYPE CONTINUOUS_OPINION\n"
            "INITIAL_OPINION_DISTRIBUTION bimodal\n"
            "\n"
            "BIN LowOpinion\n"
            "BIN HighOpinion\n"
            "\n"
            "BLOCK bounded_confidence\n"
            "TYPE OpinionDistanceThreshold\n"
            "PARAM epsilon 1.0\n"
            "\n"
            "BLOCK selection_bias\n"
            "TYPE OpinionSelectionBias\n"
            "PARAM gamma 0.0\n"
            "\n"
            "BLOCK opinion_compromise\n"
            "TYPE OpinionCompromise\n"
            "PARAM mu 0.5\n"
            "\n"
            "BLOCK opinion_normalization\n"
            "TYPE OpinionNormalization\n"
            "PARAM min 0.0\n"
            "PARAM max 1.0\n"
            "\n"
            "EXECUTE OpinionMixModel ON g1 FOR 4"
        )

        parser = ep.ExperimentParser()
        parser.set_query(query)
        parser.parse()

        local_scope = {}
        global_scope = {}
        exec(parser.script, global_scope, local_scope)

        iterations = parser.execute_query()
        self.assertIsInstance(iterations, list)
        self.assertGreaterEqual(len(iterations), 1)
        self.assertIn("status", iterations[0])
        self.assertTrue(all(0.0 <= float(v) <= 1.0 for v in iterations[0]["status"].values()))

    def test_continuous_opinion_builder_ndql_with_zealots(self):
        query = (
            "MODEL OpinionZealotModel\n"
            "TYPE CONTINUOUS_OPINION\n"
            "INITIAL_OPINION_DISTRIBUTION uniform\n"
            "\n"
            "BIN LowOpinion\n"
            "BIN HighOpinion\n"
            "\n"
            "BLOCK bounded_confidence\n"
            "TYPE OpinionDistanceThreshold\n"
            "PARAM epsilon 1.0\n"
            "\n"
            "BLOCK selection_bias\n"
            "TYPE OpinionSelectionBias\n"
            "PARAM gamma 0.0\n"
            "\n"
            "BLOCK opinion_compromise\n"
            "TYPE OpinionCompromise\n"
            "PARAM mu 0.5\n"
            "\n"
            "BLOCK opinion_normalization\n"
            "TYPE OpinionNormalization\n"
            "PARAM min 0.0\n"
            "PARAM max 1.0\n"
            "\n"
            "BLOCK opinion_zealot\n"
            "TYPE OpinionZealot\n"
            "PARAM share 1.0\n"
            "PARAM fixed_value 1.0\n"
            "\n"
            "EXECUTE OpinionZealotModel ON g1 FOR 4"
        )

        parser = ep.ExperimentParser()
        parser.set_query(query)
        parser.parse()

        local_scope = {}
        global_scope = {}
        exec(parser.script, global_scope, local_scope)

        iterations = parser.execute_query()
        self.assertIsInstance(iterations, list)
        self.assertGreaterEqual(len(iterations), 1)
        self.assertIn("status", iterations[0])
        self.assertTrue(all(0.0 <= float(v) <= 1.0 for v in iterations[0]["status"].values()))
        self.assertTrue(all(float(v) == 1.0 for v in iterations[0]["status"].values()))
