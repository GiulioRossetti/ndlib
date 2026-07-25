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
