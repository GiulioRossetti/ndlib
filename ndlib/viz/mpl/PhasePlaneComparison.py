from ndlib.viz.mpl.ComparisonViz import ComparisonPlot
import numpy as np
import os
import matplotlib as mpl
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
import future.utils

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class PhasePlaneComparison(ComparisonPlot):

    def __init__(self, model, trends, y="Infected", x="Susceptible"):
        """
        :param model: The model object
        :param trends: The computed simulation trends
        """
        super(self.__class__, self).__init__(model, trends)
        self.x = x
        self.y = y
        self.title = "Phase Plane"

    def iteration_series(self, percentile=None):

        mseries = {mn: {} for mn in self.mnames}

        i = 0
        for trend, model in zip(self.trends, self.models):
            for t in trend:
                presences = {k: [] for k in [self.x, self.y]}
                for k in t['trends']['node_count'].keys():
                    if self.srev[self.mnames[i]][k] in presences:
                        presences[self.srev[self.mnames[i]][k]].append(
                            np.array(t['trends']['node_count'][k])/model.graph.number_of_nodes())

                mseries[self.mnames[i]] = {'x': presences[self.x], 'y': presences[self.y]}
                i += 1
        return mseries

    def plot(self, filename=None, percentile=90):
        """
        Generates the plot

        :param filename: Output filename
        :param percentile: The percentile for the trend variance area
        """
        series = self.iteration_series(percentile)

        plt.plot([1, 0], [0, 1], ls="--", alpha=0.5, c="#000000")

        for name, value in future.utils.iteritems(series):
            x = value['x'][0]
            y = value['y'][0]
            plt.plot(x, y, label="%s" % name)

        plt.grid()
        plt.xlabel("%s ratio" % self.x, fontsize=22)
        plt.ylabel("%s ratio" % self.y, fontsize=22)
        plt.xlim((0, 1))
        plt.ylim((0, 1))
        plt.legend(loc="best", fontsize=10)

        plt.tight_layout()
        if filename is not None:
            plt.savefig(filename)
            plt.clf()
        else:
            plt.show()
