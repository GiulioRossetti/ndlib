from ndlib.viz.mpl.DiffusionViz import DiffusionPlot
from bokeh.palettes import Category20_9 as cols
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


class OpinionEvolution(object):

    def __init__(self, model, trends):
        """
        :param model: The model object
        :param trends: The computed simulation trends
        """
        self.model = model
        self.srev = trends
        self.ylabel = "Opinion"

    def plot(self, filename=None, percentile=90):
        """
        Generates the plot

        :param filename: Output filename
        :param percentile: The percentile for the trend variance area
        """

        descr = ""
        infos = self.model.get_info()

        for k, v in future.utils.iteritems(infos):
            descr += "%s: %s, " % (k, v)
        descr = descr[:-2].replace("_", " ")

        nodes2opinions = {}
        node2col = {}

        mx = 0
        for it in self.srev:
            sts = it['status']
            for n, v in sts.items():
                if n in nodes2opinions:
                    nodes2opinions[n].append(v)
                else:
                    nodes2opinions[n] = [v]
                    if v < 0.33:
                        node2col[n] = '#ff0000'
                    elif 0.33 <= v <= 0.66:
                        node2col[n] = '#00ff00'
                    else:
                        node2col[n] = '#0000ff'

        for k, l in future.utils.iteritems(nodes2opinions):
            mx = len(l)
            plt.plot(range(0, mx), l, lw=1, alpha=0.5, color=node2col[k])

        # plt.grid(axis="y")
        plt.title(descr)
        plt.xlabel("Iterations", fontsize=24)
        plt.ylabel(self.ylabel, fontsize=24)
        plt.legend(loc="best", fontsize=18)
        plt.xlim((0, mx))

        plt.tight_layout()
        if filename is not None:
            plt.savefig(filename)
            plt.clf()
        else:
            plt.show()