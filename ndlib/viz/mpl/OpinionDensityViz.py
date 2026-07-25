import os
import matplotlib as mpl
if os.environ.get("DISPLAY", "") == "":
    mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import future.utils

__author__ = "Antigravity"
__license__ = "BSD-2-Clause"


class OpinionDensityViz(object):
    def __init__(self, model, trends, bins=50):
        """
        :param model: The model object
        :param trends: The computed simulation trends (iterations)
        :param bins: Number of vertical bins for opinion density
        """
        self.model = model
        self.srev = trends
        self.bins = bins
        self.ylabel = "Opinion"

    def plot(self, filename=None):
        """
        Generates the plot
        :param filename: Output filename
        """
        descr = ""
        infos = self.model.get_info()
        for k, v in future.utils.iteritems(infos):
            descr += "%s: %s, " % (k, v)
        descr = descr[:-2].replace("_", " ")

        nodes2opinions = {}
        last_it = self.srev[-1]["iteration"] + 1
        last_seen = {}

        for it in self.srev:
            sts = it["status"]
            its = it["iteration"]
            for n, v in sts.items():
                if n in nodes2opinions:
                    last_id = last_seen[n]
                    last_value = nodes2opinions[n][last_id]
                    for i in range(last_id, its):
                        nodes2opinions[n][i] = last_value
                    nodes2opinions[n][its] = v
                    last_seen[n] = its
                else:
                    nodes2opinions[n] = [0.0] * last_it
                    nodes2opinions[n][its] = v
                    last_seen[n] = 0

        for n in nodes2opinions:
            last_id = last_seen[n]
            last_value = nodes2opinions[n][last_id]
            for i in range(last_id + 1, last_it):
                nodes2opinions[n][i] = last_value

        all_opinions = np.array([nodes2opinions[n] for n in nodes2opinions])
        min_op = np.min(all_opinions)
        max_op = np.max(all_opinions)
        if min_op == max_op:
            min_op -= 0.1
            max_op += 0.1

        heatmap = np.zeros((self.bins, last_it))
        bin_edges = np.linspace(min_op, max_op, self.bins + 1)

        for t in range(last_it):
            counts, _ = np.histogram(all_opinions[:, t], bins=bin_edges)
            heatmap[:, t] = counts / len(nodes2opinions)

        plt.figure(figsize=(10, 6))
        im = plt.imshow(heatmap, aspect='auto', origin='lower', extent=[0, last_it - 1, min_op, max_op], cmap='hot')
        plt.colorbar(im, label="Density")
        plt.title(descr)
        plt.xlabel("Iterations", fontsize=14)
        plt.ylabel(self.ylabel, fontsize=14)
        plt.tight_layout()

        if filename is not None:
            plt.savefig(filename)
            plt.clf()
        else:
            plt.show()
