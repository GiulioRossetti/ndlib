import abc
from bokeh.palettes import Category20_9 as cols
import matplotlib.pyplot as plt
import future.utils

__author__ = 'Giulio Rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"


class DiffusionPlot(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, model, trends):
        self.model = model
        self.trends = trends
        statuses = model.available_statuses
        self.srev = {v: k for k, v in future.utils.iteritems(statuses)}
        self.ylabel = ""
        self.title = ""

    @abc.abstractmethod
    def iteration_series(self, percentile):
        """
        Prepare the data to be visualized

        :return: a dictionary where iteration ids are keys and the associated values are the computed measures
        """
        pass

    def plot(self, filename, percentile=90):

        pres = self.iteration_series(percentile)
        infos = self.model.get_info()
        descr = ""

        for k, v in future.utils.iteritems(infos):
            descr += "%s: %s, " % (k, v)
        descr = descr[:-2].replace("_", " ")

        mx = 0
        i = 0
        for k, l in pres.iteritems():
            mx = len(l[0])
            plt.plot(range(0, mx), l[1], lw=2, label=self.srev[k], alpha=0.5, color=cols[i])
            plt.fill_between(range(0,  mx), l[0], l[2], alpha="0.2", color=cols[i])
            i += 1

        plt.grid(axis="y")
        plt.title(descr)
        plt.xlabel("Iterations", fontsize=24)
        plt.ylabel(self.ylabel, fontsize=24)
        plt.legend(loc="best", fontsize=24)
        plt.xlim((0, mx))

        plt.tight_layout()
        plt.savefig(filename)

