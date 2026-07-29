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

    def test_custom_continuous_opinion_builder_supports_opinion_blocks(self):
        from ndlib.dashboard.server import generate_custom_model_class, generate_ndql_script
        import networkx as nx
        import ndlib.models.ModelConfig as mc

        payload = {
            "name": "OpinionBlockModel",
            "use_case": "continuous_opinions",
            "template_id": "algorithmic_bias",
            "initial_opinion_distribution": {
                "family": "bimodal",
                "params": {"low": 0.2, "high": 0.8, "mix": 0.5, "sigma": 0.05},
                "bounds": [0.0, 1.0]
            },
            "epsilon": 0.8,
            "gamma": 0.0,
            "mu": 0.4,
            "statuses": [
                {"name": "LowOpinion", "code": 0},
                {"name": "HighOpinion", "code": 1}
            ],
            "compartments": [
                {"name": "distribution", "type": "OpinionDistribution", "params": {"family": "bimodal", "params": {"low": 0.2, "high": 0.8, "mix": 0.5}, "bounds": [0.0, 1.0]}},
                {"name": "stubbornness", "type": "OpinionStubbornness", "params": {"theta": 0.15}},
                {"name": "noise", "type": "OpinionNoise", "params": {"sigma": 0.02}},
                {"name": "consensus", "type": "OpinionConsensusBlock", "params": {"mode": "mean", "confidence": 0.6}},
                {"name": "assimilation", "type": "OpinionAssimilation", "params": {"rate": 0.3}},
                {"name": "repulsion", "type": "OpinionRepulsion", "params": {"strength": 0.1}},
                {"name": "bounded_drift", "type": "OpinionBoundedDrift", "params": {"step": 0.1, "bounds": [0.0, 1.0]}},
                {"name": "media_influence", "type": "OpinionMediaInfluence", "params": {"weight": 0.25, "k": 2, "media_opinions": [0.15, 0.85]}},
                {"name": "multi_topic", "type": "OpinionMultiTopic", "params": {"topics": ["economy", "health"], "coupling": 0.2}},
                {"name": "label_switch", "type": "OpinionLabelSwitch", "params": {"probability": 0.25, "triggering_status": "HighOpinion"}}
            ],
            "rules": [],
            "initial_status": [
                {"status": "LowOpinion", "ratio": 0.5},
                {"status": "HighOpinion", "ratio": 0.5}
            ]
        }

        class_code = generate_custom_model_class(payload)
        self.assertIn("OpinionDistribution", class_code)
        self.assertIn("media_count", class_code)
        self.assertIn("multi_topic_names", class_code)
        self.assertIn("consensus_mode", class_code)
        self.assertIn("bounded_drift_step", class_code)

        ndql_script = generate_ndql_script(payload)
        self.assertIn("TYPE OpinionDistribution", ndql_script)
        self.assertIn("TYPE OpinionMediaInfluence", ndql_script)
        self.assertIn("TYPE OpinionMultiTopic", ndql_script)
        self.assertIn("PARAM family bimodal", ndql_script)
        self.assertIn("PARAM k 2", ndql_script)
        self.assertIn("PARAM topics [economy,health]", ndql_script)

        local_scope = {}
        global_scope = {}
        exec(class_code, global_scope, local_scope)
        model_cls = local_scope["OpinionBlockModel"]

        model = model_cls(nx.path_graph(6))
        cfg = mc.Configuration()
        cfg.add_model_parameter("initial_opinion_distribution", {
            "family": "bimodal",
            "params": {"low": 0.2, "high": 0.8, "mix": 0.5, "sigma": 0.05},
            "bounds": [0.0, 1.0]
        })
        cfg.add_model_parameter("epsilon", 0.8)
        cfg.add_model_parameter("gamma", 0.0)
        cfg.add_model_parameter("mu", 0.4)
        cfg.add_model_parameter("assimilation_rate", 0.3)
        cfg.add_model_parameter("stubbornness", 0.15)
        cfg.add_model_parameter("noise_sigma", 0.02)
        cfg.add_model_parameter("repulsion_strength", 0.1)
        cfg.add_model_parameter("bounded_drift_step", 0.1)
        cfg.add_model_parameter("media_weight", 0.25)
        cfg.add_model_parameter("media_count", 2)
        cfg.add_model_parameter("media_opinions", [0.15, 0.85])
        cfg.add_model_parameter("consensus_mode", "mean")
        cfg.add_model_parameter("consensus_weight", 0.6)
        cfg.add_model_parameter("multi_topic_names", ["economy", "health"])
        cfg.add_model_parameter("multi_topic_coupling", 0.2)
        cfg.add_model_parameter("quantization_bins", 0)
        model.set_initial_status(cfg)
        model.status = {node: float(node) / 5.0 for node in model.status}
        model.initial_status = model.status.copy()
        model.actual_iteration = 1

        result = model.iteration()
        self.assertIn("status", result)
        self.assertTrue(all(0.0 <= float(v) <= 1.0 for v in result["status"].values()))
        self.assertTrue(all("opinion" in model.graph.nodes[node] for node in model.graph.nodes()))

    def test_hybrid_coupling_blocks_execute(self):
        from ndlib.models.compartments.NDQLBlocks import (
            AttributeCoupling,
            CommunityCoupling,
            EpidemicDependentBias,
            InfectionAffectsOpinion,
            OpinionAffectsContactRate,
            OpinionAffectsRecovery,
            OpinionAffectsInfection,
            PolicyIntervention,
            StatusDependentOpinionUpdate,
        )
        import networkx as nx

        graph = nx.path_graph(4)
        for node, com in enumerate([0, 0, 1, 1]):
            graph.nodes[node]["com"] = com
            graph.nodes[node]["opinion"] = 0.1 * (node + 1)

        status = {0: 0, 1: 1, 2: 1, 3: 0}
        params = {"model": {"iteration": 1, "available_statuses": {"Susceptible": 0, "Infected": 1}}}

        infection_risk = OpinionAffectsInfection(target="infection_risk", strength=1.0)
        infection_risk.execute(1, graph, status, status, params)
        self.assertAlmostEqual(graph.nodes[1]["infection_risk"], 0.2, places=6)

        recovery_rate = OpinionAffectsRecovery(target="recovery_rate", strength=0.5)
        recovery_rate.execute(1, graph, status, status, params)
        self.assertIn("recovery_rate", graph.nodes[1])

        contact_rate = OpinionAffectsContactRate(target="contact_rate", strength=0.5)
        contact_rate.execute(1, graph, status, status, params)
        self.assertIn("contact_rate", graph.nodes[1])

        opinion_shift = InfectionAffectsOpinion(source_statuses=[1], target=1.0, strength=1.0)
        opinion_shift.execute(1, graph, status, status, params)
        self.assertAlmostEqual(graph.nodes[1]["opinion"], 1.0, places=6)

        status_update = StatusDependentOpinionUpdate(status_filter=[1], kernel="neighbor_mean", strength=1.0)
        graph.nodes[1]["opinion"] = 0.0
        status_update.execute(1, graph, status, status, params)
        self.assertTrue(0.0 <= graph.nodes[1]["opinion"] <= 1.0)

        epidemic_bias = EpidemicDependentBias(status_filter=[1], status_weight=0.9, cross_status_factor=0.1, target="selection_bias")
        epidemic_bias.execute(1, graph, status, status, params)
        self.assertAlmostEqual(graph.nodes[1]["selection_bias"], 0.9, places=6)

        attribute_coupling = AttributeCoupling(attribute="opinion", source="opinion", target="contact_rate", strength=1.0)
        graph.nodes[0]["opinion"] = 0.7
        attribute_coupling.execute(0, graph, status, status, params)
        self.assertAlmostEqual(graph.nodes[0]["contact_rate"], 0.7, places=6)

        community_coupling = CommunityCoupling(community_field="com", intra=1.0, inter=0.0, target="opinion")
        graph.nodes[0]["opinion"] = 0.0
        graph.nodes[1]["opinion"] = 1.0
        community_coupling.execute(0, graph, status, status, params)
        self.assertAlmostEqual(graph.nodes[0]["opinion"], 1.0, places=6)

        policy = PolicyIntervention(start=0, end=2, target="policy_flag", action="set", value=1)
        policy.execute(0, graph, status, status, params)
        self.assertEqual(graph.nodes[0]["policy_flag"], 1)

    def test_epidemic_blocks_execute(self):
        from ndlib.models.compartments.NDQLBlocks import (
            CommunityMixingBlock,
            DoseResponseBlock,
            EdgeActivationBlock,
            ExposureRate,
            HospitalizationBlock,
            ImportationBlock,
            IncubationState,
            InfectionAffectsOpinion,
            LatencyPeriod,
            MortalityBlock,
            QuarantineBlock,
            RecoveryKernel,
            ReinfectionBlock,
            RewiringBlock,
            SeasonalityBlock,
            StrainBlock,
            SuperSpreaderBlock,
            TestingBlock,
            TransmissionKernel,
            TreatmentBlock,
            VaccinationBlock,
            WaningImmunity,
        )
        import networkx as nx

        graph = nx.path_graph(4)
        for node in graph.nodes():
            graph.nodes[node]["com"] = 0 if node < 2 else 1
            graph.nodes[node]["opinion"] = 0.25 * (node + 1)

        status = {0: 0, 1: 1, 2: 1, 3: 0}
        params = {"model": {"iteration": 2, "available_statuses": {"Susceptible": 0, "Infected": 1, "Removed": 2}}}

        ExposureRate(beta=0.5, contact_weight=1.0, mixing=1.0).execute(1, graph, status, status, params)
        self.assertIn("exposure", graph.nodes[1])

        TransmissionKernel(saturation=1.0).execute(1, graph, status, status, params)
        self.assertIn("transmission_probability", graph.nodes[1])

        DoseResponseBlock(shape="logistic", scale=2.0, offset=0.1).execute(1, graph, status, status, params)
        self.assertIn("infection_probability", graph.nodes[1])

        LatencyPeriod(duration=2).execute(1, graph, status, status, params)
        IncubationState(infectiousness=0.3, duration=2).execute(1, graph, status, status, params)
        RecoveryKernel(gamma=0.2).execute(1, graph, status, status, params)
        WaningImmunity(rate=0.1).execute(1, graph, status, status, params)
        VaccinationBlock(coverage=1.0, efficacy=0.8).execute(0, graph, status, status, params)
        QuarantineBlock(duration=2, coverage=1.0).execute(0, graph, status, status, params)
        TestingBlock(sensitivity=1.0, specificity=1.0).execute(1, graph, status, status, params)
        TreatmentBlock(efficacy=0.7).execute(1, graph, status, status, params)
        HospitalizationBlock(rate=1.0, mortality=0.2).execute(1, graph, status, status, params)
        MortalityBlock(fatality=1.0, target_status="Removed").execute(1, graph, status, status, params)
        ReinfectionBlock(susceptibility=0.6).execute(2, graph, status, status, params)
        StrainBlock(strain_id="A").execute(2, graph, status, status, params)
        SuperSpreaderBlock(activity=3.0, burst_rate=1.0).execute(2, graph, status, status, params)
        SeasonalityBlock(period=4, amplitude=0.5).execute(2, graph, status, status, params)
        ImportationBlock(arrival_rate=1.0, infectious_status="Infected").execute(3, graph, status, status, params)
        RewiringBlock(rewire_rate=1.0).execute(0, graph, status, status, params)
        CommunityMixingBlock(intra_rate=1.0, inter_rate=0.0).execute(0, graph, status, status, params)
        EdgeActivationBlock(threshold=1.0, duration=1).execute(0, graph, status, status, params)

        self.assertIn("vaccinated", graph.nodes[0])
        self.assertIn("quarantined", graph.nodes[0])
        self.assertIn("tested_positive", graph.nodes[1])
        self.assertIn("hospitalized", graph.nodes[1])
        self.assertIn("dead", graph.nodes[1])
        self.assertIn("strain_id", graph.nodes[2])
        self.assertIn("rewired", graph.nodes[0])
        self.assertIn("mixing_rate", graph.nodes[0])
        self.assertIn("active", graph.nodes[0])

    def test_custom_model_ndql_serializes_declarations_and_observables(self):
        from ndlib.dashboard.server import generate_custom_model_class, generate_ndql_script

        payload = {
            "name": "TypedNDQLModel",
            "statuses": [
                {"name": "Susceptible", "code": 0},
                {"name": "Infected", "code": 1}
            ],
            "declarations": [
                {"kind": "PARAM", "name": "epsilon", "type": "float", "default": 0.1},
                {"kind": "VARIABLE", "name": "opinion", "type": "continuous", "range": [0, 1], "default": 0.5},
                {"kind": "CONSTANT", "name": "tau", "type": "float", "default": 0.25},
                {"kind": "DISTRIBUTION", "name": "opinion_seed", "type": "continuous", "range": [0, 1], "default": "bimodal"},
            ],
            "observables": [
                {"variable": "opinion", "mode": "bins", "bins": 20, "range": [0, 1]}
            ],
            "compartments": [
                {
                    "name": "stoch",
                    "type": "NodeStochastic",
                    "params": {"rate": 0.1, "triggering_status": "Infected"}
                }
            ],
            "rules": [
                {"from": "Susceptible", "to": "Infected", "using": "stoch"}
            ],
            "initial_status": [
                {"status": "Susceptible", "ratio": 0.9},
                {"status": "Infected", "ratio": 0.1}
            ]
        }

        class_code = generate_custom_model_class(payload)
        self.assertIn("self.declarations = [{'kind': 'PARAM'", class_code)
        self.assertIn("self.observables = [{'variable': 'opinion'", class_code)

        ndql_script = generate_ndql_script(payload)
        self.assertIn("DECLARE PARAM epsilon TYPE float DEFAULT 0.1", ndql_script)
        self.assertIn("DECLARE VARIABLE opinion TYPE continuous RANGE [0,1] DEFAULT 0.5", ndql_script)
        self.assertIn("DECLARE CONSTANT tau TYPE float DEFAULT 0.25", ndql_script)
        self.assertIn("DECLARE DISTRIBUTION opinion_seed TYPE continuous RANGE [0,1] DEFAULT bimodal", ndql_script)
        self.assertIn("OBSERVE opinion AS bins BINS 20 RANGE [0,1]", ndql_script)

    def test_custom_model_supports_shared_execution_blocks(self):
        from ndlib.dashboard.server import generate_custom_model_class, generate_ndql_script
        import networkx as nx
        import ndlib.models.ModelConfig as mc

        payload = {
            "name": "PhaseBlocksModel",
            "statuses": [
                {"name": "Susceptible", "code": 0},
                {"name": "Infected", "code": 1},
                {"name": "Recovered", "code": 2},
            ],
            "compartments": [
                {"name": "selector_gate", "type": "Selector", "params": {"policy": "random", "share": 1.0}},
                {"name": "filter_gate", "type": "Filter", "params": {"predicate": "True"}},
                {"name": "kernel_gate", "type": "Kernel", "params": {"rate": 1.0}},
                {"name": "transform_gate", "type": "Transform", "params": {"expression": "value", "target": "opinion"}},
                {"name": "clamp_gate", "type": "ClampNormalize", "params": {"min": 0.0, "max": 1.0, "target": "opinion"}},
                {"name": "schedule_gate", "type": "Schedule", "params": {"start": 100, "end": 200}},
                {"name": "observe_gate", "type": "Observe", "params": {"variable": "opinion", "mode": "bins", "bins": 10, "range": [0, 1]}},
                {"name": "compose_gate", "type": "Compose", "params": {"condition": "selector_gate", "if_true": "filter_gate", "if_false": "kernel_gate"}},
            ],
            "rules": [
                {"from": "Susceptible", "to": "Infected", "using": "compose_gate"},
                {"from": "Infected", "to": "Recovered", "using": "kernel_gate"},
            ],
            "initial_status": [
                {"status": "Susceptible", "ratio": 0.9},
                {"status": "Infected", "ratio": 0.1},
                {"status": "Recovered", "ratio": 0.0},
            ]
        }

        class_code = generate_custom_model_class(payload)
        self.assertNotIn("_GenericBlock", class_code)
        self.assertIn("selector_gate = Selector(policy='random', share=1.0)", class_code)
        self.assertIn("compose_gate = Compose(condition=selector_gate, if_true=filter_gate, if_false=kernel_gate)", class_code)
        self.assertIn("kernel_gate = Kernel(rate=1.0)", class_code)

        ndql_script = generate_ndql_script(payload)
        self.assertIn("TYPE Compose", ndql_script)
        self.assertIn("TYPE Selector", ndql_script)
        self.assertIn("TYPE Kernel", ndql_script)

        scope = {}
        exec(class_code, scope, scope)
        model_cls = scope["PhaseBlocksModel"]
        model = model_cls(nx.path_graph(8))
        cfg = mc.Configuration()
        cfg.add_model_parameter("percentage_Susceptible", 0.9)
        cfg.add_model_parameter("percentage_Infected", 0.1)
        cfg.add_model_parameter("percentage_Recovered", 0.0)
        model.set_initial_status(cfg)
        result = model.iteration()
        self.assertIn("status", result)

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
