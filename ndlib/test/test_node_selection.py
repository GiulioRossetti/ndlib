from __future__ import absolute_import

import unittest

import networkx as nx

import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics as epd
from ndlib.node_selection import STRATEGIES, rank_nodes, select_nodes


def _reference_ci(g, radius=2):
    """Collective influence by breadth-first search, for checking."""
    out = {}
    for n in g:
        dist = nx.single_source_shortest_path_length(g, n, cutoff=radius)
        frontier = [m for m, d in dist.items() if d == radius]
        out[n] = max(g.degree(n) - 1, 0) * sum(max(g.degree(m) - 1, 0) for m in frontier)
    return out


def _hub_and_clique():
    # K5 on 0-4 (coreness 4); hub 10 with 8 leaves (degree 9, coreness 1), tied to node 0
    g = nx.complete_graph(5)
    g.add_edges_from((10, leaf) for leaf in range(11, 19))
    g.add_edge(10, 0)
    return g


class NodeSelectionTest(unittest.TestCase):
    def test_degree_betweenness_pagerank_pick_star_centre(self):
        g = nx.star_graph(6)
        for strategy in ("degree", "betweenness", "pagerank"):
            self.assertEqual(select_nodes(g, 1, strategy), [0], strategy)

    def test_betweenness_picks_bridge(self):
        g = nx.barbell_graph(5, 1)  # node 5 joins the two cliques
        self.assertEqual(select_nodes(g, 1, "betweenness"), [5])

    def test_kcore_prefers_dense_core_over_degree_hub(self):
        g = _hub_and_clique()
        self.assertEqual(select_nodes(g, 1, "degree"), [10])
        self.assertEqual(select_nodes(g, 1, "kcore"), [0])
        self.assertEqual(set(select_nodes(g, 5, "kcore")), set(range(5)))

    def test_collective_influence_matches_bfs_reference_adaptively(self):
        g = nx.gnm_random_graph(80, 200, seed=3)
        order = select_nodes(g, 12, "collective_influence")
        h = g.copy()
        for picked in order:
            ref = _reference_ci(h)
            self.assertEqual(ref[picked], max(ref.values()))
            h.remove_edges_from(list(h.edges(picked)))  # removed nodes keep no links
        self.assertEqual(len(set(order)), 12)

    def test_collective_influence_on_path(self):
        g = nx.path_graph(5)  # CI_2 is 1 for nodes 1 and 3, 0 elsewhere
        self.assertIn(select_nodes(g, 1, "collective_influence")[0], (1, 3))

    def test_validation_and_determinism(self):
        g = nx.karate_club_graph()
        self.assertEqual(select_nodes(g, 0, "degree"), [])
        with self.assertRaises(ValueError):
            select_nodes(g, 35, "degree")
        with self.assertRaises(ValueError):
            rank_nodes(g, "no_such_strategy")
        for strategy in STRATEGIES:
            first = select_nodes(g, 4, strategy, seed=7)
            self.assertEqual(first, select_nodes(g, 4, strategy, seed=7), strategy)
            self.assertEqual(len(set(first)), 4)
        self.assertNotEqual(select_nodes(g, 8, "random", seed=1), select_nodes(g, 8, "random", seed=2))

    def test_directed_and_self_loops_are_simplified(self):
        g = nx.DiGraph([(0, 1), (0, 2), (0, 3), (1, 1)])
        self.assertEqual(select_nodes(g, 1, "degree"), [0])
        self.assertEqual(select_nodes(g, 1, "kcore"), [0])

    def test_immunized_nodes_never_infected_in_sir(self):
        g = nx.erdos_renyi_graph(200, 0.05, seed=4)
        immune = select_nodes(g, 20, "degree")
        model = epd.SIRModel(g, seed=11)
        cfg = mc.Configuration()
        cfg.add_model_parameter("beta", 0.3)
        cfg.add_model_parameter("gamma", 0.1)
        cfg.add_model_parameter("fraction_infected", 0.05)
        cfg.add_model_initial_configuration("Removed", immune)
        model.set_initial_status(cfg)
        for n in immune:
            self.assertEqual(model.status[n], 2)
        model.iteration_bunch(30, node_status=False)
        for n in immune:
            self.assertEqual(model.status[n], 2)


if __name__ == "__main__":
    unittest.main()
