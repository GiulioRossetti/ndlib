import abc
from bokeh.plotting import figure
from bokeh.models import Title
from bokeh.palettes import Category20_9 as cols
import future.utils
import six

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


@six.add_metaclass(abc.ABCMeta)
class DiffusionPlot(object):
    # __metaclass__ = abc.ABCMeta

    def __init__(self, model, trends):
        self.model = model
        self.trends = trends
        statuses = model.available_statuses
        self.srev = {v: k for k, v in future.utils.iteritems(statuses)}
        self.ylabel = ""
        self.title = ""
        self.nnodes = model.graph.number_of_nodes()
        self.normalized = True

    @abc.abstractmethod
    def iteration_series(self, percentile=100):
        """
        Prepare the data to be visualized

        :param percentile: The percentile for the trend variance area
        :return: a dictionary where iteration ids are keys and the associated values are the computed measures
        """
        pass

    def plot(self, percentile=100, width=500, height=500):
        """
        Generates the plot

        :param percentile: The percentile for the trend variance area
        :param width: Image width. Default 500px.
        :param height: Image height. Default 500px.
        :return: a bokeh figure image
        """
        pres = self.iteration_series(percentile)
        infos = self.model.get_info()
        descr = ""
        for k, v in future.utils.iteritems(infos):
            descr += "%s: %s, " % (k, v)
        descr = descr[:-2].replace("_", " ")

        p = figure(width=width, height=height)
        i = 0
        for k, l in future.utils.iteritems(pres):

            mx = len(l[0])
            if self.normalized:
                p.line(range(0, mx), l[1] / self.nnodes, line_width=2, legend=self.srev[k], alpha=0.5, color=cols[i])
            else:
                p.line(range(0, mx), l[1], line_width=2, legend=self.srev[k], alpha=0.5, color=cols[i])

            i += 1

        p.xaxis.axis_label = 'Iterations'
        p.title.text = "%s - %s" % (self.model.get_name(), self.title)
        p.yaxis.axis_label = self.ylabel
        p.ygrid[0].grid_line_alpha = 0.5
        p.xgrid[0].grid_line_alpha = 0.5
        p.add_layout(Title(text=descr, align="center"), "below")
        p.legend.orientation = "horizontal"

        return p