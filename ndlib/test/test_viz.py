from __future__ import absolute_import

import unittest

import networkx as nx
from bokeh.models.layouts import Column
from bokeh.plotting.figure import Figure
from ndlib.viz.bokeh.DiffusionPrevalence import DiffusionPrevalence
from ndlib.viz.bokeh.MultiPlot import MultiPlot

import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics.SIRModel as sir
from ndlib.viz.bokeh.DiffusionTrend import DiffusionTrend


class VizTest(unittest.TestCase):

    def test_visualize(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = sir.SIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.001)
        config.add_model_parameter('gamma', 0.01)
        config.add_model_parameter("percentage_infected", 0.05)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(200)
        viz = DiffusionTrend(model, iterations)
        p = viz.plot()
        self.assertIsInstance(p, Figure)

    def test_visualize_prevalence(self):
        g = nx.erdos_renyi_graph(1000, 0.1)
        model = sir.SIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.001)
        config.add_model_parameter('gamma', 0.01)
        config.add_model_parameter("percentage_infected", 0.05)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(200)
        viz = DiffusionPrevalence(model, iterations)
        p = viz.plot()
        self.assertIsInstance(p, Figure)

    def test_multi(self):

        vm = MultiPlot()

        g = nx.erdos_renyi_graph(1000, 0.1)
        model = sir.SIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.001)
        config.add_model_parameter('gamma', 0.01)
        config.add_model_parameter("percentage_infected", 0.05)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(200)
        viz = DiffusionTrend(model, iterations)
        p = viz.plot()

        vm.add_plot(p)

        g = nx.erdos_renyi_graph(1000, 0.1)
        model = sir.SIRModel(g)
        config = mc.Configuration()
        config.add_model_parameter('beta', 0.001)
        config.add_model_parameter('gamma', 0.01)
        config.add_model_parameter("percentage_infected", 0.05)
        model.set_initial_status(config)
        iterations = model.iteration_bunch(200)
        viz = DiffusionPrevalence(model, iterations)
        p1 = viz.plot()

        vm.add_plot(p1)
        m = vm.plot()
        self.assertIsInstance(m, Column)


if __name__ == '__main__':
    unittest.main()
