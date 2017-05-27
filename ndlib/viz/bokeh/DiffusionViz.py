import abc
from bokeh.plotting import figure
from bokeh.models import Title
from bokeh.palettes import Category20_9 as cols
import future.utils

__author__ = 'Giulio Rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"


class DiffusionPlot(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, model, iterations):
        self.model = model
        self.iterations = iterations
        statuses = model.available_statuses
        self.srev = {v: k for k, v in future.utils.iteritems(statuses)}
        self.ylabel = ""
        self.title = ""

    @abc.abstractmethod
    def iteration_series(self):
        pass

    def plot(self, width=500, height=500):
        """
        :param width: Image width. Default 500px.
        :param height: Image height. Default 500px.
        :return: a bokeh figure image
        """
        pres = self.iteration_series()
        infos = self.model.getinfo()
        descr = ""
        for k, v in future.utils.iteritems(infos):
            descr += "%s: %s, " % (k, v)
        descr = descr[:-2].replace("_", " ")

        p = figure(width=width, height=height)
        i = 0
        for k, l in pres.iteritems():
            p.line(range(0, len(l)), l, line_width=2, color=cols[i], legend=self.srev[k])
            i += 1

        p.xaxis.axis_label = 'Iterations'
        p.title.text = "%s - %s" % (self.model.get_name(), self.title)
        p.yaxis.axis_label = self.ylabel
        p.ygrid[0].grid_line_alpha = 0.5
        p.xgrid[0].grid_line_alpha = 0.5
        p.add_layout(Title(text=descr, align="center"), "below")
        p.legend.orientation = "horizontal"

        return p
