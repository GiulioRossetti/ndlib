from DiffusionViz import DiffusionPlot
import future.utils

__author__ = 'Giulio Rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"


class DiffusionTrend(DiffusionPlot):

    def __init__(self, model, iterations):
        """
        :param model: The model object
        :param iterations: The computed simulation iterations
        """
        super(self.__class__, self).__init__(model, iterations)
        self.ylabel = "#Nodes"
        self.title = "Diffusion Trend"

    def iteration_series(self):
        initial_status = self.iterations[0]['status']
        presences = {k: [0] for k in self.srev.keys()}
        for nid in initial_status:
            presences[initial_status[nid]][0] += 1

        c = 1
        for i in self.iterations[1:]:
            for p in presences:
                presences[p].append(presences[p][c - 1])
            actual_status = i['status']
            for nid, v in future.utils.iteritems(actual_status):
                st = initial_status[nid]
                presences[st][c] -= 1
                presences[v][c] += 1
                initial_status[nid] = v

            c += 1
        return presences
