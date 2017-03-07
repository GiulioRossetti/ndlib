from bokeh.layouts import gridplot
from bokeh.plotting import figure, show
from bokeh.models import Title
from bokeh.palettes import Category20_9 as cols

__author__ = 'Giulio Rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"


class VisualizeDiffusion(object):

    def __init__(self, model, iterations):
        self.model = model
        self.iterations = iterations
        statuses = model.available_statuses
        self.srev = {v: k for k, v in statuses.iteritems()}

    def __iteration_series(self):

        initial_status = self.iterations[0]['status']
        presences = {k: [0] for k in self.srev.keys()}
        for nid in initial_status:
            presences[initial_status[nid]][0] += 1

        c = 1
        for i in self.iterations[1:]:
            for p in presences:
                presences[p].append(presences[p][c - 1])
            actual_status = i['status']
            for nid, v in actual_status.iteritems():
                st = initial_status[nid]
                presences[st][c] -= 1
                presences[v][c] += 1
                initial_status[nid] = v

            c += 1
        return presences

    def plot(self, width=500, height=500):
        pres = self.__iteration_series()
        infos = self.model.getinfo()
        descr = ""
        for k, v in infos.iteritems():
            descr += "%s: %s, " % (k, v)
        descr = descr[:-2].replace("_", " ")

        p = figure(width=width, height=height)
        i = 0
        for k, l in pres.iteritems():
            p.line(range(0, len(l)), l, line_width=2, color=cols[i], legend=self.srev[k])
            i += 1

        p.title.text = self.model.get_name()
        p.xaxis.axis_label = 'Iterations'
        p.yaxis.axis_label = '#Nodes'
        p.ygrid[0].grid_line_alpha = 0.5
        p.xgrid[0].grid_line_alpha = 0.5
        p.add_layout(Title(text=descr, align="center"), "below")
        p.legend.orientation = "horizontal"

        return p


class MultiPlot(object):

    def __init__(self):
        self.plots = []

    def add_plot(self, p):
        self.plots.append(p)

    def plot(self):
        grid = gridplot(self.plots, ncols=2)
        return grid
