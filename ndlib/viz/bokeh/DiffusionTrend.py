from ndlib.viz.bokeh.DiffusionViz import DiffusionPlot
import numpy as np

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class DiffusionTrend(DiffusionPlot):

    def __init__(self, model, trends):
        """
        :param model: The model object
        :param iterations: The computed simulation iterations
        """
        super(self.__class__, self).__init__(model, trends)
        self.ylabel = "#Nodes"
        self.title = "Diffusion Trend"

    def iteration_series(self, percentile=100):
        series = {k: [] for k in self.srev.keys()}

        presences = {k: [] for k in self.srev.keys()}
        for t in self.trends:

            for st in t:
                for k in t[st]['node_count']:
                    presences[k].append(np.array(t[st]['node_count'][k]))

        for st in presences:
            tp = np.percentile(np.array(presences[st]), percentile, axis=0)
            bp = np.percentile(np.array(presences[st]), 100 - percentile, axis=0)
            av = np.average(np.array(presences[st]), axis=0)
            series[st] = (tp, av, bp)

        return series
