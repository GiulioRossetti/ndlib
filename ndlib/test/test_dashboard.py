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

