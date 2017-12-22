from ndlib.viz.mpl.ComparisonViz import ComparisonPlot
import numpy as np

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class DiffusionTrendComparison(ComparisonPlot):

    def __init__(self, models, trends, statuses=("Infected")):
        """
        :param models: A list of model object
        :param trends: A list of computed simulation trends
        :param statuses: The model statuses for which make the plot. Default ["Infected"].
        """
        super(self.__class__, self).__init__(models, trends, statuses)
        self.ylabel = "% Nodes"
        self.title = "Diffusion Trend"

    def iteration_series(self, percentile):

        mseries = {mn: {} for mn in self.mnames}

        i = 0
        for trend in self.trends:
            presences = {k: [] for k in self.classes}
            for t in trend:
                for k in t['trends']['node_count'].keys():
                    if self.srev[self.mnames[i]][k] in presences:
                        presences[self.srev[self.mnames[i]][k]].append(np.array(t['trends']['node_count'][k]))

            for st in presences:
                tp = np.percentile(np.array(presences[st]), percentile, axis=0)
                bp = np.percentile(np.array(presences[st]), 100-percentile, axis=0)
                av = np.average(np.array(presences[st]), axis=0)
                if self.mnames[i] not in mseries:
                    mseries[self.mnames[i]] = {st: (tp, av, bp)}
                else:
                    mseries[self.mnames[i]][st] = (tp, av, bp)
            i += 1

        return mseries
