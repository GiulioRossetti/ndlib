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

    def test_continuous_opinion_builder_ndql_supports_opinion_blocks(self):
        query = (
            "MODEL OpinionPhase3Model\n"
            "TYPE CONTINUOUS_OPINION\n"
            "INITIAL_OPINION_DISTRIBUTION {\"family\":\"gaussian\",\"params\":{\"mean\":0.4,\"sigma\":0.1},\"bounds\":[0,1]}\n"
            "\n"
            "BIN LowOpinion\n"
            "BIN HighOpinion\n"
            "\n"
            "BLOCK distribution\n"
            "TYPE OpinionDistribution\n"
            "PARAM family gaussian\n"
            "PARAM params {\"mean\":0.4,\"sigma\":0.1}\n"
            "PARAM bounds [0,1]\n"
            "\n"
            "BLOCK stubbornness\n"
            "TYPE OpinionStubbornness\n"
            "PARAM theta 0.1\n"
            "\n"
            "BLOCK noise\n"
            "TYPE OpinionNoise\n"
            "PARAM sigma 0.02\n"
            "\n"
            "BLOCK consensus\n"
            "TYPE OpinionConsensusBlock\n"
            "PARAM mode mean\n"
            "PARAM confidence 0.5\n"
            "\n"
            "BLOCK assimilation\n"
            "TYPE OpinionAssimilation\n"
            "PARAM rate 0.3\n"
            "\n"
            "BLOCK repulsion\n"
            "TYPE OpinionRepulsion\n"
            "PARAM strength 0.1\n"
            "\n"
            "BLOCK bounded_drift\n"
            "TYPE OpinionBoundedDrift\n"
            "PARAM step 0.1\n"
            "PARAM bounds [0,1]\n"
            "\n"
            "BLOCK media_influence\n"
            "TYPE OpinionMediaInfluence\n"
            "PARAM weight 0.2\n"
            "PARAM k 2\n"
            "PARAM media_opinions [0.1,0.9]\n"
            "\n"
            "BLOCK multi_topic\n"
            "TYPE OpinionMultiTopic\n"
            "PARAM topics [economy,health]\n"
            "PARAM coupling 0.2\n"
            "\n"
            "BLOCK label_switch\n"
            "TYPE OpinionLabelSwitch\n"
            "PARAM probability 0.25\n"
            "\n"
            "EXECUTE OpinionPhase3Model ON g1 FOR 4"
        )

        parser = ep.ExperimentParser()
        parser.set_query(query)
        parser.parse()

        self.assertIn("OpinionDistribution", parser.script)
        self.assertIn("OpinionMediaInfluence", parser.script)
        self.assertIn("OpinionLabelSwitch", parser.script)

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

    def test_continuous_opinion_builder_ndql_with_declarations_and_observables(self):
        query = (
            "MODEL TypedNDQLModel\n"
            "TYPE CONTINUOUS_OPINION\n"
            "INITIAL_OPINION_DISTRIBUTION normal\n"
            "\n"
            "DECLARE PARAM epsilon TYPE float DEFAULT 0.1\n"
            "DECLARE VARIABLE opinion TYPE continuous RANGE [0,1] DEFAULT 0.5\n"
            "\n"
            "BIN LowOpinion\n"
            "BIN HighOpinion\n"
            "\n"
            "BLOCK bounded_confidence\n"
            "TYPE OpinionDistanceThreshold\n"
            "PARAM epsilon 0.1\n"
            "\n"
            "BLOCK opinion_normalization\n"
            "TYPE OpinionNormalization\n"
            "PARAM min 0.0\n"
            "PARAM max 1.0\n"
            "\n"
            "OBSERVE opinion AS bins BINS 20 RANGE [0,1]\n"
            "\n"
            "EXECUTE TypedNDQLModel ON g1 FOR 3"
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

    def test_legacy_ndql_supports_shared_blocks(self):
        query = (
            "CREATE_NETWORK g1\n"
            "TYPE erdos_renyi_graph\n"
            "PARAM n 20\n"
            "PARAM p 0.2\n"
            "\n"
            "MODEL phase_model\n"
            "\n"
            "STATUS Susceptible\n"
            "\n"
            "STATUS Infected\n"
            "\n"
            "STATUS Recovered\n"
            "\n"
            "DECLARE PARAM epsilon TYPE float DEFAULT 0.1\n"
            "OBSERVE opinion AS bins BINS 10 RANGE [0,1]\n"
            "\n"
            "COMPARTMENT selector_gate\n"
            "TYPE Selector\n"
            "PARAM policy random\n"
            "PARAM share 1.0\n"
            "\n"
            "COMPARTMENT filter_gate\n"
            "TYPE Filter\n"
            "PARAM predicate True\n"
            "\n"
            "COMPARTMENT kernel_gate\n"
            "TYPE Kernel\n"
            "PARAM rate 1.0\n"
            "\n"
            "COMPARTMENT clamp_gate\n"
            "TYPE ClampNormalize\n"
            "PARAM min 0.0\n"
            "PARAM max 1.0\n"
            "PARAM target opinion\n"
            "\n"
            "COMPARTMENT compose_gate\n"
            "TYPE Compose\n"
            "PARAM condition selector_gate\n"
            "PARAM if_true filter_gate\n"
            "PARAM if_false kernel_gate\n"
            "\n"
            "RULE\n"
            "FROM Susceptible\n"
            "TO Infected\n"
            "USING compose_gate\n"
            "\n"
            "RULE\n"
            "FROM Infected\n"
            "TO Recovered\n"
            "USING kernel_gate\n"
            "\n"
            "INITIALIZE\n"
            "SET Susceptible 0.9\n"
            "SET Infected 0.1\n"
            "SET Recovered 0.0\n"
            "\n"
            "EXECUTE phase_model ON g1 FOR 3"
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
        self.assertIn("trends", iterations[0])
