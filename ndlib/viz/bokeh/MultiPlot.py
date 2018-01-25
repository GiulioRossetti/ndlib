from bokeh.layouts import gridplot

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class MultiPlot(object):

    def __init__(self):
        self.plots = []

    def add_plot(self, plot):
        """
        :param plot: The bokeh plot to add to the grid
        """
        self.plots.append(plot)

    def plot(self, ncols=2):
        """
        :param ncols: Number of grid columns
        :return: a bokeh figure image
        """
        grid = gridplot(self.plots, ncols=ncols)
        return grid
