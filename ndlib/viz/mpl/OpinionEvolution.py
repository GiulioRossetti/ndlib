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

    def plot(self, filename=None):
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

        last_it = self.srev[-1]['iteration'] + 1
        last_seen = {}

        for it in self.srev:
            sts = it['status']
            its = it['iteration']
            for n, v in sts.items():
                if n in nodes2opinions:
                    last_id = last_seen[n]
                    last_value = nodes2opinions[n][last_id]

                    for i in range(last_id, its):
                        nodes2opinions[n][i] = last_value

                    nodes2opinions[n][its] = v
                    last_seen[n] = its
                else:
                    nodes2opinions[n] = [0]*last_it
                    nodes2opinions[n][its] = v
                    last_seen[n] = 0
                    if v < 0.33:
                        node2col[n] = '#ff0000'
                    elif 0.33 <= v <= 0.66:
                        node2col[n] = '#00ff00'
                    else:
                        node2col[n] = '#0000ff'

        mx = 0
        for k, l in future.utils.iteritems(nodes2opinions):
            if mx < last_seen[k]:
                mx = last_seen[k]
            x = list(range(0, last_seen[k]))
            y = l[0:last_seen[k]]
            plt.plot(x, y, lw=1, alpha=0.5, color=node2col[k])

        plt.title(descr)
        plt.xlabel("Iterations", fontsize=24)
        plt.ylabel(self.ylabel, fontsize=24)
        plt.legend(loc="best", fontsize=18)

        plt.tight_layout()
        if filename is not None:
            plt.savefig(filename)
            plt.clf()
        else:
            plt.show()