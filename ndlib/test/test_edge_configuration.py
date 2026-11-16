from __future__ import absolute_import

import unittest
import warnings

import networkx as nx

import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics as epd


def _cascade(graph, thresholds, infected, seed=1):
    model = epd.IndependentCascadesModel(graph, seed=seed)
    config = mc.Configuration()
    for edge, value in thresholds.items():
        config.add_edge_configuration("threshold", edge, value)
    config.add_model_initial_configuration("Infected", infected)
    model.set_initial_status(config)
    return model


class EdgeConfigurationTest(unittest.TestCase):
    def test_both_orientations_on_undirected_graph(self):
        # issue #262: one value per direction used to be dropped silently
        g = nx.karate_club_graph()
        thresholds = {}
        for u, v in g.edges():
            thresholds[(u, v)] = 1.0 / g.degree(v)
            thresholds[(v, u)] = 1.0 / g.degree(u)
        model = _cascade(g, thresholds, [0])
        self.assertEqual(len(model.params["edges"]["threshold"]), 2 * g.number_of_edges())
        self.assertAlmostEqual(model.params["edges"]["threshold"][(0, 1)], 1.0 / g.degree(1))
        self.assertAlmostEqual(model.params["edges"]["threshold"][(1, 0)], 1.0 / g.degree(0))

    def test_direction_specific_values_are_used(self):
        g = nx.path_graph(2)
        model = _cascade(g, {(0, 1): 1.0, (1, 0): 0.0}, [0])
        model.iteration_bunch(3, node_status=False)
        self.assertEqual(model.status[1], 2)  # 0 always passes to 1
        model = _cascade(g, {(0, 1): 1.0, (1, 0): 0.0}, [1])
        model.iteration_bunch(3, node_status=False)
        self.assertEqual(model.status[0], 0)  # 1 never passes to 0

    def test_one_value_per_edge_still_works(self):
        g = nx.path_graph(4)
        model = _cascade(g, {e: 0.3 for e in g.edges()}, [0])
        self.assertEqual(model.params["edges"]["threshold"], {e: 0.3 for e in g.edges()})

    def test_partial_configuration_warns_and_is_ignored(self):
        g = nx.path_graph(4)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model = _cascade(g, {(0, 1): 0.5}, [0])
        self.assertNotIn("threshold", model.params["edges"])
        self.assertTrue(any("not set for every edge" in str(w.message) for w in caught))


if __name__ == "__main__":
    unittest.main()
