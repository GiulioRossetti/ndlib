from __future__ import absolute_import

import unittest

import networkx as nx
from bokeh.models.layouts import Column
from bokeh.plotting.figure import Figure
from ndlib.viz.bokeh.DiffusionPrevalence import DiffusionPrevalence
from ndlib.viz.bokeh.MultiPlot import MultiPlot

import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics as epd
from ndlib.viz.bokeh.DiffusionTrend import DiffusionTrend

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class VizTest(unittest.TestCase):

    def test_visualize(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.SIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.001)
        config.add_model_parameter('gamma', 0.01)
        config.add_model_parameter("fraction_infected", 0.05)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(200)
        trends = model.build_trends(iterations)
        viz = DiffusionTrend(model, trends)
        p = viz.plot()
        self.assertIsInstance(p, Figure)

    def test_visualize_prevalence(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.SIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.001)
        config.add_model_parameter('gamma', 0.01)
        config.add_model_parameter("fraction_infected", 0.05)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(200)
        trends = model.build_trends(iterations)
        viz = DiffusionPrevalence(model, trends)
        p = viz.plot()
        self.assertIsInstance(p, Figure)

    def test_multi(self):

        vm = MultiPlot()

        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.SIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.001)
        config.add_model_parameter('gamma', 0.01)
        config.add_model_parameter("fraction_infected", 0.05)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(200)
        trends = model.build_trends(iterations)
        viz = DiffusionTrend(model, trends)
        p = viz.plot()

        vm.add_plot(p)

        g = nx.erdos_renyi_graph(1000, 0.1)
        model = epd.SIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.001)
        config.add_model_parameter('gamma', 0.01)
        config.add_model_parameter("fraction_infected", 0.05)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(200)
        trends = model.build_trends(iterations)
        viz = DiffusionPrevalence(model, trends)
        p1 = viz.plot()

        vm.add_plot(p1)
        m = vm.plot()
        self.assertIsInstance(m, Column)


if __name__ == '__main__':
    unittest.main()
