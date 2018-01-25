import abc
from bokeh.palettes import Category20_9 as cols
import os
import matplotlib as mpl
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
import future.utils
import past
import six

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class InitializationException(Exception):
    """Initialization Exception"""


@six.add_metaclass(abc.ABCMeta)
class ComparisonPlot(object):
    # __metaclass__ = abc.ABCMeta

    def __init__(self, models, trends, statuses=["Infected"]):
        self.models = models
        self.trends = trends
        if len(models) != len(trends):
            raise InitializationException({"message": "The number of models does not match the number of trends"})

        sts = [model.available_statuses for model in models]
        self.mnames = ["%s_%s" % (models[i].name, i) for i in past.builtins.xrange(0, len(models))]
        self.srev = {}
        i = 0

        available_classes = {}
        for model in models:
            srev = {v: k for k, v in future.utils.iteritems(sts[i])}
            self.nnodes = model.graph.number_of_nodes()
            for cl in srev.values():
                available_classes[cl] = None

            self.srev["%s_%s" % (model.name, i)] = srev
            i += 1

        if type(statuses) == list:
            cls = set(statuses) & set(available_classes.keys())
        else:
            cls = set([statuses]) & set(available_classes.keys())
        if len(cls) > 0:
            self.classes = cls
        else:
            raise InitializationException({"message": "Statuses specified not available for the model (or missing)"})

        self.ylabel = ""
        self.title = ""
        self.normalized = True


    @abc.abstractmethod
    def iteration_series(self, percentile):
        """
        Prepare the data to be visualized

        :param percentile: The percentile for the trend variance area
        :return: a dictionary where iteration ids are keys and the associated values are the computed measures.
        """
        pass

    def plot(self, filename=None, percentile=90):
        """
        Plot the comparison on file.

        :param filename: the output filename
        :param percentile: The percentile for the trend variance area. Default 90.

        """

        pres = self.iteration_series(percentile)

        mx = 0
        i, h = 0, 0
        for k, l in future.utils.iteritems(pres):
            j = 0
            for st in l:
                mx = len(l[st][0])
                if self.normalized:
                    plt.plot(range(0, mx), l[st][1]/self.nnodes, lw=2,
                             label="%s - %s" % (k.split("_")[0], st), alpha=0.9, color=cols[h+j])
                    plt.fill_between(range(0,  mx), l[st][0]/self.nnodes,
                                     l[st][2]/self.nnodes, alpha=0.2, color=cols[h+j])
                else:
                    plt.plot(range(0, mx), l[st][1], lw=2,
                             label="%s - %s" % (k.split("_")[0], st), alpha=0.9, color=cols[h + j])
                    plt.fill_between(range(0, mx), l[st][0],
                                     l[st][2], alpha=0.2, color=cols[h + j])
                j += 1
            i += 1
            h += 2

        plt.grid(axis="y")
        plt.xlabel("Iterations", fontsize=24)
        plt.ylabel(self.ylabel, fontsize=24)
        plt.legend(loc="best", fontsize=18)
        plt.xlim((0, mx))

        if self.normalized:
            plt.ylim((0, 1))

        plt.tight_layout()
        
        if filename is not None:
            plt.savefig(filename)
            plt.clf()
        else:
            plt.show()
