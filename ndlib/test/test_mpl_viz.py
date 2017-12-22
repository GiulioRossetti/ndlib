from __future__ import absolute_import

import unittest
import past
import networkx as nx
import dynetx as dn
from ndlib.viz.mpl.DiffusionPrevalence import DiffusionPrevalence
from ndlib.viz.mpl.PrevalenceComparison import DiffusionPrevalenceComparison
from ndlib.viz.mpl.TrendComparison import DiffusionTrendComparison

import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics.SIRModel as sir
import ndlib.models.epidemics.SIModel as si
import ndlib.models.dynamic.DynSIModel as dsi
from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend
import os

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class MplVizTest(unittest.TestCase):

    def test_visualize(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = sir.SIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.001)
        config.add_model_parameter('gamma', 0.01)
        config.add_model_parameter("percentage_infected", 0.05)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(200)
        trends = model.build_trends(iterations)

        # Visualization
        viz = DiffusionTrend(model, trends)
        viz.plot("diffusion.pdf")
        os.remove("diffusion.pdf")

    def test_visualize_dynamic(self):
        dg = dn.DynGraph()

        for t in past.builtins.xrange(0, 4):
            g = nx.erdos_renyi_graph(200, 0.05)
            dg.add_interactions_from(g.edges(), t)

        model = dsi.DynSIModel(dg)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.1)
        config.add_model_parameter("percentage_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.execute_snapshots()
        trends = model.build_trends(iterations)

        # Visualization
        viz = DiffusionPrevalence(model, trends)
        viz.plot("prevd.pdf")
        os.remove("prevd.pdf")

    def test_visualize_prevalence(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = sir.SIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.001)
        config.add_model_parameter('gamma', 0.01)
        config.add_model_parameter("percentage_infected", 0.05)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(200)
        trends = model.build_trends(iterations)

        # Visualization
        viz = DiffusionPrevalence(model, trends)
        viz.plot("prev.pdf")
        os.remove("prev.pdf")

    def test_prevalence_comparison(self):

        # Network topology
        g = nx.erdos_renyi_graph(1000, 0.1)

        # Model selection
        model = sir.SIRModel(g)

        # Model Configuration
        cfg = mc.Configuration()
        cfg.add_model_parameter('beta', 0.001)
        cfg.add_model_parameter('gamma', 0.02)
        cfg.add_model_parameter("percentage_infected", 0.01)
        model.set_initial_status(cfg)

        iterations = model.iteration_bunch(200)
        trends = model.build_trends(iterations)

        model1 = si.SIModel(g)
        cfg = mc.Configuration()
        cfg.add_model_parameter('beta', 0.001)
        cfg.add_model_parameter("percentage_infected", 0.01)
        model1.set_initial_status(cfg)

        iterations = model1.iteration_bunch(200)
        trends1 = model1.build_trends(iterations)

        viz = DiffusionPrevalenceComparison([model, model1], [trends, trends1])
        viz.plot("prev_comparison.pdf")
        os.remove("prev_comparison.pdf")

    def test_trend_comparison(self):

        # Network topology
        g = nx.erdos_renyi_graph(1000, 0.1)

        # Model selection
        model = sir.SIRModel(g)

        # Model Configuration
        cfg = mc.Configuration()
        cfg.add_model_parameter('beta', 0.001)
        cfg.add_model_parameter('gamma', 0.02)
        cfg.add_model_parameter("percentage_infected", 0.01)
        model.set_initial_status(cfg)

        iterations = model.iteration_bunch(200)
        trends = model.build_trends(iterations)

        model1 = si.SIModel(g)
        cfg = mc.Configuration()
        cfg.add_model_parameter('beta', 0.001)
        cfg.add_model_parameter("percentage_infected", 0.01)
        model1.set_initial_status(cfg)

        iterations = model1.iteration_bunch(200)
        trends1 = model1.build_trends(iterations)

        viz = DiffusionTrendComparison([model, model1], [trends, trends1])

        viz.plot("trend_comparison.pdf")
        os.remove("trend_comparison.pdf")

if __name__ == '__main__':
    unittest.main()
