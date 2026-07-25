import os
import matplotlib as mpl
if os.environ.get("DISPLAY", "") == "":
    mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import future.utils

__author__ = "Antigravity"
__license__ = "BSD-2-Clause"


class PhasePortraitViz(object):
    def __init__(self, model, trends, status_x="Susceptible", status_y="Infected"):
        """
        :param model: The model object
        :param trends: The computed simulation trends
        :param status_x: Name of the status for the X-axis
        :param status_y: Name of the status for the Y-axis
        """
        self.model = model
        self.trends = trends
        self.statuses = model.available_statuses
        self.srev = {v: k for k, v in future.utils.iteritems(self.statuses)}
        
        if status_x not in self.statuses:
            raise ValueError("Status %s not available in model" % status_x)
        if status_y not in self.statuses:
            raise ValueError("Status %s not available in model" % status_y)

        self.status_x_code = self.statuses[status_x]
        self.status_y_code = self.statuses[status_y]
        self.status_x_name = status_x
        self.status_y_name = status_y
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

        # Collect node counts across runs
        counts_x = []
        counts_y = []

        for t in self.trends:
            if "trends" in t and "node_count" in t["trends"]:
                node_counts = t["trends"]["node_count"]
                val_x = node_counts.get(self.status_x_code, node_counts.get(str(self.status_x_code)))
                val_y = node_counts.get(self.status_y_code, node_counts.get(str(self.status_y_code)))
                if val_x is not None and val_y is not None:
                    counts_x.append(val_x)
                    counts_y.append(val_y)

        if not counts_x or not counts_y:
            raise ValueError("No trend data found for the specified statuses")

        av_x = np.average(np.array(counts_x), axis=0) / self.nnodes
        av_y = np.average(np.array(counts_y), axis=0) / self.nnodes
        T = len(av_x)

        plt.figure(figsize=(8, 6))
        # Plot the trajectory line
        plt.plot(av_x, av_y, color="purple", lw=2, label="Trajectory")
        
        # Draw gradient colors or scatter dots to show direction of time
        sc = plt.scatter(av_x, av_y, c=range(T), cmap="viridis", s=40, zorder=3)
        plt.colorbar(sc, label="Iterations / Time")

        # Mark start and end points
        plt.scatter(av_x[0], av_y[0], color="green", s=100, label="Start", zorder=4)
        plt.scatter(av_x[-1], av_y[-1], color="red", s=100, label="End", zorder=4)

        plt.title("Phase Portrait: %s vs %s\n%s" % (self.status_x_name, self.status_y_name, descr), fontsize=12)
        plt.xlabel(self.status_x_name, fontsize=12)
        plt.ylabel(self.status_y_name, fontsize=12)
        plt.grid(True)
        plt.legend(loc="best")
        plt.tight_layout()

        if filename is not None:
            plt.savefig(filename)
            plt.clf()
        else:
            plt.show()
