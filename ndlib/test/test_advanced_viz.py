import unittest
import os
import networkx as nx

from ndlib.viz.mpl.OpinionDensityViz import OpinionDensityViz
from ndlib.viz.mpl.PolarizationMetricsViz import PolarizationMetricsViz
from ndlib.viz.mpl.PhasePortraitViz import PhasePortraitViz
from ndlib.viz.mpl.PeakMetricsViz import PeakMetricsViz
from ndlib.viz.mpl.TransmissionTreeViz import TransmissionTreeViz

import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics as epd
import ndlib.models.opinions as op


class AdvancedVizTest(unittest.TestCase):
    def test_opinion_viz(self):
        g = nx.erdos_renyi_graph(100, 0.1)
        model = op.FJModel(g)
        config = mc.Configuration()
        config.add_model_parameter("init_dist_lower", -0.5)
        config.add_model_parameter("init_dist_upper", 0.5)
        for node in g.nodes():
            config.add_node_configuration("stubbornness", node, 0.2)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)

        # 1. OpinionDensityViz
        viz_density = OpinionDensityViz(model, iterations, bins=10)
        viz_density.plot("opinion_density.pdf")
        self.assertTrue(os.path.exists("opinion_density.pdf"))
        os.remove("opinion_density.pdf")

        # 2. PolarizationMetricsViz
        viz_polarization = PolarizationMetricsViz(model, iterations)
        viz_polarization.plot("polarization_metrics.pdf")
        self.assertTrue(os.path.exists("polarization_metrics.pdf"))
        os.remove("polarization_metrics.pdf")

    def test_epidemics_viz(self):
        g = nx.erdos_renyi_graph(100, 0.1)
        model = epd.SIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter("beta", 0.1)
        config.add_model_parameter("gamma", 0.05)
        config.add_model_parameter("fraction_infected", 0.1)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(10)
        trends = model.build_trends(iterations)

        # 3. PhasePortraitViz
        viz_phase = PhasePortraitViz(model, trends)
        viz_phase.plot("phase_portrait.pdf")
        self.assertTrue(os.path.exists("phase_portrait.pdf"))
        os.remove("phase_portrait.pdf")

        # 4. PeakMetricsViz
        viz_peak = PeakMetricsViz(model, trends)
        viz_peak.plot("peak_metrics.pdf")
        self.assertTrue(os.path.exists("peak_metrics.pdf"))
        os.remove("peak_metrics.pdf")

        # 5. TransmissionTreeViz
        viz_tree = TransmissionTreeViz(model, iterations)
        viz_tree.plot("transmission_tree.pdf")
        self.assertTrue(os.path.exists("transmission_tree.pdf"))
        os.remove("transmission_tree.pdf")
