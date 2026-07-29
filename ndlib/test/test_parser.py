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

    def test_hybrid_coupling_ndql_roundtrip(self):
        query = (
            "CREATE_NETWORK g1\n"
            "TYPE erdos_renyi_graph\n"
            "PARAM n 20\n"
            "PARAM p 0.2\n"
            "\n"
            "MODEL CoupledModel\n"
            "\n"
            "STATUS Susceptible\n"
            "STATUS Infected\n"
            "STATUS Recovered\n"
            "\n"
            "COMPARTMENT attr_couple\n"
            "TYPE AttributeCoupling\n"
            "PARAM source opinion\n"
            "PARAM target infection_risk\n"
            "PARAM strength 1.0\n"
            "\n"
            "COMPARTMENT infect_shift\n"
            "TYPE InfectionAffectsOpinion\n"
            "PARAM source_statuses [1]\n"
            "PARAM target 1.0\n"
            "PARAM strength 1.0\n"
            "\n"
            "COMPARTMENT policy\n"
            "TYPE PolicyIntervention\n"
            "PARAM start 0\n"
            "PARAM end 2\n"
            "PARAM target policy_flag\n"
            "PARAM action set\n"
            "PARAM value 1\n"
            "\n"
            "COMPARTMENT community\n"
            "TYPE CommunityCoupling\n"
            "PARAM community_field com\n"
            "PARAM intra 1.0\n"
            "PARAM inter 0.0\n"
            "PARAM target opinion\n"
            "\n"
            "RULE\n"
            "FROM Susceptible\n"
            "TO Infected\n"
            "USING attr_couple\n"
            "\n"
            "RULE\n"
            "FROM Infected\n"
            "TO Recovered\n"
            "USING infect_shift\n"
            "\n"
            "INITIALIZE\n"
            "SET Susceptible 0.5\n"
            "SET Infected 0.5\n"
            "SET Recovered 0.0\n"
            "\n"
            "EXECUTE CoupledModel ON g1 FOR 3"
        )

        parser = ep.ExperimentParser()
        parser.set_query(query)
        parser.parse()

        self.assertIn("AttributeCoupling", parser.script)
        self.assertIn("InfectionAffectsOpinion", parser.script)
        self.assertIn("PolicyIntervention", parser.script)
        self.assertIn("CommunityCoupling", parser.script)

        local_scope = {}
        global_scope = {}
        exec(parser.script, global_scope, local_scope)
        iterations = parser.execute_query()
        self.assertIsInstance(iterations, list)
        self.assertGreaterEqual(len(iterations), 1)
        self.assertIn("trends", iterations[0])

    def test_epidemic_blocks_ndql_roundtrip(self):
        query = (
            "CREATE_NETWORK g1\n"
            "TYPE erdos_renyi_graph\n"
            "PARAM n 20\n"
            "PARAM p 0.2\n"
            "\n"
            "MODEL EpidemicBlocksModel\n"
            "\n"
            "STATUS Susceptible\n"
            "STATUS Infected\n"
            "STATUS Removed\n"
            "\n"
            "COMPARTMENT exposure\n"
            "TYPE ExposureRate\n"
            "PARAM beta 0.5\n"
            "PARAM contact_weight 1.0\n"
            "PARAM mixing 1.0\n"
            "\n"
            "COMPARTMENT transmission\n"
            "TYPE TransmissionKernel\n"
            "PARAM saturation 1.0\n"
            "PARAM source exposure\n"
            "\n"
            "COMPARTMENT dose\n"
            "TYPE DoseResponseBlock\n"
            "PARAM shape logistic\n"
            "PARAM scale 2.0\n"
            "PARAM offset 0.1\n"
            "\n"
            "COMPARTMENT recovery\n"
            "TYPE RecoveryKernel\n"
            "PARAM gamma 0.2\n"
            "\n"
            "COMPARTMENT quarantine\n"
            "TYPE QuarantineBlock\n"
            "PARAM duration 2\n"
            "PARAM coverage 1.0\n"
            "\n"
            "COMPARTMENT vaccination\n"
            "TYPE VaccinationBlock\n"
            "PARAM coverage 1.0\n"
            "PARAM efficacy 0.8\n"
            "\n"
            "COMPARTMENT mortality\n"
            "TYPE MortalityBlock\n"
            "PARAM fatality 1.0\n"
            "PARAM target_status Removed\n"
            "\n"
            "RULE\n"
            "FROM Susceptible\n"
            "TO Infected\n"
            "USING exposure\n"
            "\n"
            "RULE\n"
            "FROM Infected\n"
            "TO Removed\n"
            "USING recovery\n"
            "\n"
            "INITIALIZE\n"
            "SET Susceptible 0.9\n"
            "SET Infected 0.1\n"
            "SET Removed 0.0\n"
            "\n"
            "EXECUTE EpidemicBlocksModel ON g1 FOR 3"
        )

        parser = ep.ExperimentParser()
        parser.set_query(query)
        parser.parse()

        self.assertIn("ExposureRate", parser.script)
        self.assertIn("RecoveryKernel", parser.script)
        self.assertIn("MortalityBlock", parser.script)

        local_scope = {}
        global_scope = {}
        exec(parser.script, global_scope, local_scope)

        iterations = parser.execute_query()
        self.assertIsInstance(iterations, list)
        self.assertGreaterEqual(len(iterations), 1)
        self.assertIn("trends", iterations[0])

    def test_utility_blocks_ndql_roundtrip(self):
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write('{"graph": {"source": "imported"}, "nodes": {"0": {"label": "seed"}}}')
            graph_path = fh.name

        try:
            query = (
                "CREATE_NETWORK g1\n"
                "TYPE erdos_renyi_graph\n"
                "PARAM n 12\n"
                "PARAM p 0.2\n"
                "\n"
                "MODEL UtilityBlocksModel\n"
                "\n"
                "STATUS Susceptible\n"
                "STATUS Infected\n"
                "\n"
                "COMPARTMENT seed_selection\n"
                "TYPE SeedSelection\n"
                "PARAM nodes [0,1]\n"
                "\n"
                "COMPARTMENT role_assignment\n"
                "TYPE NodeRoleAssignment\n"
                "PARAM role zealot\n"
                "PARAM nodes [0,1]\n"
                "\n"
                "COMPARTMENT attr_init\n"
                "TYPE AttributeInitializer\n"
                "PARAM attribute opinion\n"
                "PARAM value 0.25\n"
                "\n"
                "COMPARTMENT graph_import\n"
                "TYPE GraphImport\n"
                "PARAM source %s\n"
                "PARAM merge True\n"
                "\n"
                "COMPARTMENT community\n"
                "TYPE CommunityAssignment\n"
                "PARAM algorithm greedy_modularity_communities\n"
                "PARAM target com\n"
                "\n"
                "COMPARTMENT alias\n"
                "TYPE RuleAlias\n"
                "PARAM alias infection_rule\n"
                "PARAM target infection\n"
                "PARAM description Reusable rule\n"
                "\n"
                "COMPARTMENT preview\n"
                "TYPE PreviewObservable\n"
                "PARAM variable opinion\n"
                "PARAM mode bins\n"
                "PARAM bins 10\n"
                "PARAM range [0,1]\n"
                "\n"
                "COMPARTMENT hint\n"
                "TYPE ValidationHint\n"
                "PARAM name opinion_range\n"
                "PARAM minimum 0.0\n"
                "PARAM maximum 1.0\n"
                "PARAM target opinion\n"
                "\n"
                "COMPARTMENT infection\n"
                "TYPE NodeStochastic\n"
                "PARAM rate 0.1\n"
                "TRIGGER Infected\n"
                "\n"
                "RULE\n"
                "FROM Susceptible\n"
                "TO Infected\n"
                "USING infection\n"
                "\n"
                "INITIALIZE\n"
                "SET Infected 0.1\n"
                "\n"
                "EXECUTE UtilityBlocksModel ON g1 FOR 3" % graph_path
            )

            parser = ep.ExperimentParser()
            parser.set_query(query)
            parser.parse()

            self.assertIn("SeedSelection", parser.script)
            self.assertIn("GraphImport", parser.script)
            self.assertIn("ValidationHint", parser.script)

            local_scope = {}
            global_scope = {}
            exec(parser.script, global_scope, local_scope)

            iterations = parser.execute_query()
            self.assertIsInstance(iterations, list)
            self.assertGreaterEqual(len(iterations), 1)
            self.assertIn("trends", iterations[0])
        finally:
            try:
                os.remove(graph_path)
            except OSError:
                pass

    def test_phase6_ndql_updates_roundtrip(self):
        query = (
            "MODEL Phase6UpdateModel\n"
            "TYPE CONTINUOUS_OPINION\n"
            "INITIAL_OPINION_DISTRIBUTION uniform\n"
            "\n"
            "DECLARE GLOBAL simulation_name TYPE string DEFAULT phase6\n"
            "DECLARE EDGE_VARIABLE edge_weight TYPE float DEFAULT 1.0\n"
            "\n"
            "BIN LowOpinion\n"
            "BIN HighOpinion\n"
            "\n"
            "BLOCK opinion_normalization\n"
            "TYPE OpinionNormalization\n"
            "PARAM min 0.0\n"
            "PARAM max 1.0\n"
            "\n"
            "WHEN iteration >= 0\n"
            "SCHEDULE 0 10 PERIOD 1 PHASE 0\n"
            "UPDATE opinion = 1.0\n"
            "\n"
            "EXECUTE Phase6UpdateModel ON g1 FOR 3"
        )

        parser = ep.ExperimentParser()
        parser.set_query(query)
        parser.parse()

        self.assertIn("'kind': 'GLOBAL'", parser.script)
        self.assertIn("'kind': 'EDGE_VARIABLE'", parser.script)
        self.assertIn("self.update_rules", parser.script)
        self.assertIn("when", parser.script)

        local_scope = {}
        global_scope = {}
        exec(parser.script, global_scope, local_scope)
        iterations = parser.execute_query()
        self.assertIsInstance(iterations, list)
        self.assertGreaterEqual(len(iterations), 2)
        self.assertTrue(all(float(v) == 1.0 for v in iterations[-1]["status"].values()))

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
