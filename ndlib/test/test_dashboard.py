import unittest
from ndlib.dashboard.server import discover_models

__author__ = "Antigravity"
__license__ = "BSD-2-Clause"


class DashboardTest(unittest.TestCase):
    def test_discover_models(self):
        models = discover_models()
        self.assertIsInstance(models, dict)
        
        # Verify that common models are discovered
        self.assertIn("SIRModel", models)
        self.assertIn("FJModel", models)
        
        # Verify schema of discovered models
        sir = models["SIRModel"]
        self.assertEqual(sir["category"], "Epidemics")
        self.assertEqual(sir["name"], "SIR")
        self.assertIn("beta", sir["parameters"]["model"])
        self.assertIn("gamma", sir["parameters"]["model"])
        self.assertIn("Susceptible", sir["statuses"])
        
        fj = models["FJModel"]
        self.assertEqual(fj["category"], "Opinions")
        self.assertEqual(fj["name"], "Friedkin-Johnsen")
        self.assertIn("stubbornness", fj["parameters"]["nodes"])

        epidemic_labels = [meta["name"] for meta in models.values() if meta["category"] == "Epidemics"]
        self.assertEqual(len(epidemic_labels), len(set(epidemic_labels)))
        self.assertEqual(models["SIRModel"]["display_group"], "Core Epidemic Models")
        self.assertEqual(models["SEIRctModel"]["name"], "SEIR (ct)")
        self.assertEqual(models["SEISctModel"]["name"], "SEIS (ct)")

        opinion_labels = [meta["name"] for meta in models.values() if meta["category"] == "Opinions"]
        self.assertEqual(len(opinion_labels), len(set(opinion_labels)))
        self.assertEqual(models["AlgorithmicBiasModel"]["display_group"], "Continuous Opinion Models")
        self.assertEqual(models["MajorityRuleModel"]["display_group"], "Discrete Opinion Models")
        self.assertEqual(models["AlgorithmicBiasModel"]["name"], "Algorithmic Bias")
        self.assertEqual(models["AlgorithmicBiasMediaModel"]["name"], "Algorithmic Bias and Media")
        self.assertIn("initial_opinion_distribution", models["AlgorithmicBiasModel"]["parameters"]["model"])
        self.assertIn("media_opinions", models["AlgorithmicBiasMediaModel"]["parameters"]["model"])
        self.assertNotIn("init_dist_lower", models["AlgorithmicBiasModel"]["parameters"]["model"])
        self.assertNotIn("init_dist_upper", models["AlgorithmicBiasModel"]["parameters"]["model"])

    def test_custom_model_compilation(self):
        from ndlib.dashboard.server import generate_custom_model_class, generate_ndql_script
        payload = {
            "name": "TestExtendedModel",
            "statuses": [
                {"name": "S", "code": 0},
                {"name": "I", "code": 1},
                {"name": "R", "code": 2}
            ],
            "compartments": [
                {
                    "name": "stoch",
                    "type": "NodeStochastic",
                    "params": {"rate": 0.1, "triggering_status": "I"}
                },
                {
                    "name": "attr_cat",
                    "type": "NodeCategoricalAttribute",
                    "params": {"attribute": "gender", "value": "female", "probability": 0.8}
                },
                {
                    "name": "attr_num",
                    "type": "NodeNumericalAttribute",
                    "params": {"attribute": "age", "op": "IN", "value": "18,65", "probability": 1.0}
                },
                {
                    "name": "opinion_gate",
                    "type": "NodeNumericalVariable",
                    "params": {"var": "opinion", "var_type": "ATTRIBUTE", "value": 0.5, "op": ">=", "probability": 1.0}
                },
                {
                    "name": "cond",
                    "type": "ConditionalComposition",
                    "params": {
                        "condition": "stoch",
                        "first_branch": "attr_cat",
                        "second_branch": "attr_num"
                    }
                }
            ],
            "rules": [
                {"from": "S", "to": "I", "using": "cond"}
            ],
            "initial_status": []
        }
        
        # Test class generation
        class_code = generate_custom_model_class(payload)
        self.assertIn("class TestExtendedModel(CompositeModel):", class_code)
        self.assertIn("stoch = NodeStochastic(rate=0.1, triggering_status='I')", class_code)
        self.assertIn("attr_num = NodeNumericalAttribute(attribute='age', op='IN', value=[18.0, 65.0], probability=1.0)", class_code)
        self.assertIn("opinion_gate = NodeNumericalVariable(var='opinion', var_type=NumericalType.ATTRIBUTE, value=0.5, op='>=', probability=1.0)", class_code)
        self.assertIn("cond = ConditionalComposition(condition=stoch, first_branch=attr_cat, second_branch=attr_num)", class_code)
        
        # Verify it compiles
        local_scope = {}
        global_scope = {}
        try:
            exec(class_code, global_scope, local_scope)
        except Exception as e:
            self.fail("Generated custom model code failed to compile: %s" % e)
            
        model_cls = local_scope.get("TestExtendedModel")
        self.assertIsNotNone(model_cls)
        
        # Test NDQL generation
        ndql_script = generate_ndql_script(payload)
        self.assertIn("MODEL TestExtendedModel", ndql_script)
        self.assertIn("IF stoch THEN attr_cat ELSE attr_num AS cond", ndql_script)
        self.assertIn("COMPARTMENT opinion_gate", ndql_script)

    def test_custom_opinion_model_initialization_without_infected(self):
        from ndlib.dashboard.server import generate_custom_model_class
        import networkx as nx
        import ndlib.models.ModelConfig as mc

        payload = {
            "name": "OpinionOnlyModel",
            "statuses": [
                {"name": "Agree", "code": 0},
                {"name": "Disagree", "code": 1}
            ],
            "compartments": [],
            "rules": [],
            "initial_status": [
                {"status": "Agree", "ratio": 0.6},
                {"status": "Disagree", "ratio": 0.4}
            ]
        }

        class_code = generate_custom_model_class(payload)
        self.assertNotIn("super(OpinionOnlyModel, self).set_initial_status(configuration)", class_code)

        local_scope = {}
        global_scope = {}
        exec(class_code, global_scope, local_scope)
        model_cls = local_scope["OpinionOnlyModel"]

        model = model_cls(nx.path_graph(10))
        cfg = mc.Configuration()
        cfg.add_model_parameter("percentage_Agree", 0.6)
        cfg.add_model_parameter("percentage_Disagree", 0.4)

        model.set_initial_status(cfg)
        agree = model.available_statuses["Agree"]
        disagree = model.available_statuses["Disagree"]
        self.assertEqual(sum(1 for v in model.status.values() if v == agree) + sum(1 for v in model.status.values() if v == disagree), 10)

    def test_custom_continuous_opinion_builder_initializes_opinion_attributes(self):
        from ndlib.dashboard.server import generate_custom_model_class, generate_ndql_script
        import networkx as nx
        import ndlib.models.ModelConfig as mc

        payload = {
            "name": "AlgorithmicBiasStarter",
            "use_case": "continuous_opinions",
            "template_id": "algorithmic_bias",
            "initial_opinion_distribution": "bimodal",
            "epsilon": 1.0,
            "gamma": 0.0,
            "mu": 0.5,
            "statuses": [
                {"name": "LowOpinion", "code": 0},
                {"name": "HighOpinion", "code": 1}
            ],
            "compartments": [
                {
                    "name": "bounded_confidence",
                    "type": "OpinionDistanceThreshold",
                    "params": {
                        "epsilon": 1.0
                    }
                },
                {
                    "name": "selection_bias",
                    "type": "OpinionSelectionBias",
                    "params": {
                        "gamma": 0.0
                    }
                },
                {
                    "name": "opinion_compromise",
                    "type": "OpinionCompromise",
                    "params": {
                        "mu": 0.5
                    }
                },
                {
                    "name": "opinion_normalization",
                    "type": "OpinionNormalization",
                    "params": {
                        "min": 0.0,
                        "max": 1.0
                    }
                },
                {
                    "name": "opinion_noise",
                    "type": "OpinionNoise",
                    "params": {
                        "sigma": 0.0
                    }
                }
            ],
            "rules": [],
            "initial_status": [
                {"status": "LowOpinion", "ratio": 0.5},
                {"status": "HighOpinion", "ratio": 0.5}
            ]
        }

        class_code = generate_custom_model_class(payload)
        self.assertIn("continuous_blocks", class_code)
        self.assertIn("sample_initial_opinions", class_code)

        local_scope = {}
        global_scope = {}
        exec(class_code, global_scope, local_scope)
        model_cls = local_scope["AlgorithmicBiasStarter"]

        model = model_cls(nx.path_graph(12))
        cfg = mc.Configuration()
        cfg.add_model_parameter("initial_opinion_distribution", "bimodal")
        cfg.add_model_parameter("epsilon", 1.0)
        cfg.add_model_parameter("gamma", 0.0)
        cfg.add_model_parameter("mu", 0.5)
        model.set_initial_status(cfg)

        model.status = {0: 0.0, 1: 1.0}
        model.initial_status = model.status.copy()
        model.actual_iteration = 1
        result = model.iteration()
        self.assertTrue(all(0.0 <= float(v) <= 1.0 for v in result["status"].values()))
        self.assertAlmostEqual(result["status"][0], 0.5, places=6)
        self.assertAlmostEqual(result["status"][1], 0.5, places=6)

    def test_custom_continuous_opinion_builder_supports_zealots(self):
        from ndlib.dashboard.server import generate_custom_model_class, generate_ndql_script
        import networkx as nx
        import ndlib.models.ModelConfig as mc

        payload = {
            "name": "AlgorithmicBiasWithZealots",
            "use_case": "continuous_opinions",
            "template_id": "algorithmic_bias",
            "initial_opinion_distribution": "uniform",
            "epsilon": 1.0,
            "gamma": 0.0,
            "mu": 0.5,
            "statuses": [
                {"name": "LowOpinion", "code": 0},
                {"name": "HighOpinion", "code": 1}
            ],
            "compartments": [
                {
                    "name": "bounded_confidence",
                    "type": "OpinionDistanceThreshold",
                    "params": {
                        "epsilon": 1.0
                    }
                },
                {
                    "name": "selection_bias",
                    "type": "OpinionSelectionBias",
                    "params": {
                        "gamma": 0.0
                    }
                },
                {
                    "name": "opinion_compromise",
                    "type": "OpinionCompromise",
                    "params": {
                        "mu": 0.5
                    }
                },
                {
                    "name": "opinion_normalization",
                    "type": "OpinionNormalization",
                    "params": {
                        "min": 0.0,
                        "max": 1.0
                    }
                },
                {
                    "name": "opinion_zealot",
                    "type": "OpinionZealot",
                    "params": {
                        "share": 1.0,
                        "fixed_value": 1.0
                    }
                }
            ],
            "rules": [],
            "initial_status": [
                {"status": "LowOpinion", "ratio": 0.5},
                {"status": "HighOpinion", "ratio": 0.5}
            ]
        }

        class_code = generate_custom_model_class(payload)
        self.assertIn("zealot_nodes", class_code)
        self.assertIn("zealot_share", class_code)
        self.assertIn("zealot_value", class_code)

        ndql_script = generate_ndql_script(payload)
        self.assertIn("TYPE OpinionZealot", ndql_script)
        self.assertIn("PARAM share 1.0", ndql_script)
        self.assertIn("PARAM fixed_value 1.0", ndql_script)

        local_scope = {}
        global_scope = {}
        exec(class_code, global_scope, local_scope)
        model_cls = local_scope["AlgorithmicBiasWithZealots"]

        model = model_cls(nx.path_graph(6))
        cfg = mc.Configuration()
        cfg.add_model_parameter("initial_opinion_distribution", "uniform")
        cfg.add_model_parameter("epsilon", 1.0)
        cfg.add_model_parameter("gamma", 0.0)
        cfg.add_model_parameter("mu", 0.5)
        cfg.add_model_parameter("zealot_share", 1.0)
        cfg.add_model_parameter("zealot_value", 1.0)
        model.set_initial_status(cfg)

        self.assertTrue(all(float(v) == 1.0 for v in model.status.values()))
        result = model.iteration()
        self.assertTrue(all(float(v) == 1.0 for v in result["status"].values()))
        self.assertIn("TYPE OpinionNoise", ndql_script)

    def test_build_initial_status_assignment_respects_percentages(self):
        from ndlib.dashboard.server import build_initial_status_assignment
        import networkx as nx

        graph = nx.path_graph(10)
        available_statuses = {"Agree": 0, "Disagree": 1}
        assignment = build_initial_status_assignment(
            graph,
            available_statuses,
            {"Agree": 70, "Disagree": 30}
        )

        self.assertEqual(len(assignment), 10)
        agree_count = sum(1 for status in assignment.values() if status == "Agree")
        disagree_count = sum(1 for status in assignment.values() if status == "Disagree")
        self.assertEqual(agree_count + disagree_count, 10)
        self.assertGreaterEqual(agree_count, disagree_count)

    def test_normalize_iteration_record_tuple_payload(self):
        from ndlib.dashboard.server import normalize_iteration_record

        raw = (
            3,
            (
                {0: 1, 1: 0},
                {0: 8, 1: 2},
                {0: 1, 1: -1},
            ),
        )

        normalized = normalize_iteration_record(raw)
        self.assertEqual(normalized["iteration"], 3)
        self.assertEqual(normalized["status"], {0: 1, 1: 0})
        self.assertEqual(normalized["node_count"], {0: 8, 1: 2})
        self.assertEqual(normalized["status_delta"], {0: 1, 1: -1})

    def test_coerce_model_parameter_value_handles_none(self):
        from ndlib.dashboard.server import coerce_model_parameter_value

        gamma_info = {"descr": "Algorithmic bias", "range": [0, 100], "optional": False}
        epsilon_info = {"descr": "Bounded confidence threshold", "range": [0, 1], "optional": False}
        dist_info = {
            "descr": "Initial opinion distribution in [0, 1]",
            "choices": [{"value": "uniform", "label": "Uniform"}],
            "optional": True,
            "default": "uniform",
        }

        self.assertEqual(coerce_model_parameter_value("gamma", None, gamma_info), 0.1)
        self.assertEqual(coerce_model_parameter_value("epsilon", None, epsilon_info), 0.1)
        self.assertEqual(coerce_model_parameter_value("initial_opinion_distribution", None, dist_info), "uniform")

    def test_build_absolute_status_history_reconstructs_sparse_updates(self):
        from ndlib.dashboard.server import build_absolute_status_history

        iterations = [
            {"status": {"0": 0.2, "1": 0.8, "2": 0.4}},
            {"status": {"1": 0.6}},
            {"status": {"0": 0.3, "2": 0.5}},
            {"status": {}},
        ]
        nodes = [{"id": "0"}, {"id": "1"}, {"id": "2"}]

        history = build_absolute_status_history(iterations, nodes)
        self.assertEqual(history[0], {"0": 0.2, "1": 0.8, "2": 0.4})
        self.assertEqual(history[1], {"0": 0.2, "1": 0.6, "2": 0.4})
        self.assertEqual(history[2], {"0": 0.3, "1": 0.6, "2": 0.5})
        self.assertEqual(history[3], {"0": 0.3, "1": 0.6, "2": 0.5})

    def test_build_initial_status_assignment_balances_percentages(self):
        from ndlib.dashboard.server import build_initial_status_assignment
        import networkx as nx

        graph = nx.path_graph(10)
        available_statuses = {"Susceptible": 0, "Infected": 1}
        assignment = build_initial_status_assignment(
            graph,
            available_statuses,
            {"Susceptible": 25, "Infected": 75},
        )

        self.assertEqual(len(assignment), 10)
        infected_count = sum(1 for status in assignment.values() if status == "Infected")
        susceptible_count = sum(1 for status in assignment.values() if status == "Susceptible")
        self.assertEqual(infected_count + susceptible_count, 10)
        self.assertGreater(infected_count, susceptible_count)
