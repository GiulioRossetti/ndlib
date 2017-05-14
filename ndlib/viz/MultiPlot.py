from bokeh.layouts import gridplot

__author__ = 'Giulio Rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"


class MultiPlot(object):

    def __init__(self):
        self.plots = []

    def add_plot(self, p):
        self.plots.append(p)

    def plot(self):
        grid = gridplot(self.plots, ncols=2)
        return grid
