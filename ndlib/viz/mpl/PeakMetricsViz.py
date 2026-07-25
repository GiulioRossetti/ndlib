import os
import matplotlib as mpl
if os.environ.get("DISPLAY", "") == "":
    mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import future.utils

__author__ = "Antigravity"
__license__ = "BSD-2-Clause"


class PeakMetricsViz(object):
    def __init__(self, model, trends, status_infected="Infected"):
        """
        :param model: The model object
        :param trends: The computed simulation trends (multiple runs)
        :param status_infected: Name of the status corresponding to infected/active compartment
        """
        self.model = model
        self.trends = trends
        self.statuses = model.available_statuses
        if status_infected not in self.statuses:
            raise ValueError("Status %s not available in model" % status_infected)
        self.status_code = self.statuses[status_infected]
        self.status_name = status_infected
        self.nnodes = model.graph.number_of_nodes()

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

        peaks = []
        durations = []

        for t in self.trends:
            if "trends" in t and "node_count" in t["trends"]:
                node_counts = t["trends"]["node_count"]
                val_infected = node_counts.get(self.status_code, node_counts.get(str(self.status_code)))
                if val_infected is not None:
                    peaks.append(max(val_infected) / self.nnodes)
                    duration = len(val_infected) - 1
                    for idx, val in enumerate(val_infected):
                        if val == 0:
                            duration = idx
                            break
                    durations.append(duration)

        if not peaks:
            raise ValueError("No trend data found for the specified status")

        fig, axs = plt.subplots(1, 2, figsize=(10, 5))

        # Peak Infection Fraction Boxplot
        axs[0].boxplot(peaks, patch_artist=True, boxprops=dict(facecolor="lightblue"))
        axs[0].set_title("Peak Fraction (%s)" % self.status_name)
        axs[0].set_ylabel("Fraction of Population")
        axs[0].set_xticklabels(["Simulation Runs"])
        axs[0].grid(True, axis="y")

        # Outbreak Duration Boxplot
        axs[1].boxplot(durations, patch_artist=True, boxprops=dict(facecolor="lightgreen"))
        axs[1].set_title("Outbreak Duration")
        axs[1].set_ylabel("Iterations")
        axs[1].set_xticklabels(["Simulation Runs"])
        axs[1].grid(True, axis="y")

        fig.suptitle(descr, fontsize=10)
        plt.tight_layout()

        if filename is not None:
            plt.savefig(filename)
            plt.clf()
        else:
            plt.show()
