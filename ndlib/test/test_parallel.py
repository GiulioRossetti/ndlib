import unittest
import networkx as nx
import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics as epd
from ndlib.utils import multi_runs

__author__ = "Giulio Rossetti"
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class ParallelTest(unittest.TestCase):
    def test_multi(self):

        # Network topology
        g = nx.erdos_renyi_graph(1000, 0.1)

        # Model selection
        model1 = epd.SIRModel(g)

        # Model Configuration
        config = mc.Configuration()
        config.add_model_parameter("beta", 0.001)
        config.add_model_parameter("gamma", 0.01)
        config.add_model_parameter("fraction_infected", 0.05)
        model1.set_initial_status(config)

        # Simulation multiple execution
        trends = multi_runs(
            model1,
            execution_number=10,
            iteration_number=100,
            infection_sets=None,
            nprocesses=4,
        )
        self.assertIsNotNone(trends)

    def test_multi_initial_set(self):
        # Network topology
        g = nx.erdos_renyi_graph(1000, 0.1)

        # Model selection
        model1 = epd.SIRModel(g)

        # Model Configuration
        config = mc.Configuration()
        config.add_model_parameter("beta", 0.001)
        config.add_model_parameter("gamma", 0.01)
        model1.set_initial_status(config)

        # Simulation multiple execution
        infection_sets = [
            (1, 2, 3, 4, 5),
            (3, 23, 22, 54, 2),
            (98, 2, 12, 26, 3),
            (4, 6, 9),
        ]
        trends = multi_runs(
            model1,
            execution_number=4,
            iteration_number=100,
            infection_sets=infection_sets,
            nprocesses=4,
        )
        self.assertIsNotNone(trends)


if __name__ == "__main__":
    unittest.main()
