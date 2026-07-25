import os
import matplotlib as mpl
if os.environ.get("DISPLAY", "") == "":
    mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import future.utils

__author__ = "Antigravity"
__license__ = "BSD-2-Clause"


class PolarizationMetricsViz(object):
    def __init__(self, model, trends):
        """
        :param model: The model object
        :param trends: The computed simulation trends (iterations)
        """
        self.model = model
        self.srev = trends

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

        all_opinions = np.array([nodes2opinions[n] for n in nodes2opinions]) # shape: (N, T)
        N, T = all_opinions.shape

        std_devs = []
        entropies = []
        mean_pairwise_diffs = []

        for t in range(T):
            ops = all_opinions[:, t]
            
            # 1. Standard Deviation
            std_devs.append(np.std(ops))

            # 2. Entropy (binned in 10 bins)
            counts, _ = np.histogram(ops, bins=10)
            probs = counts / N
            probs = probs[probs > 0]
            entropy = -np.sum(probs * np.log(probs))
            entropies.append(entropy)

            # 3. Mean Pairwise Absolute Difference
            # P = sum(|x_i - x_j|) / N^2
            diff_matrix = np.abs(ops[:, None] - ops[None, :])
            mean_pairwise_diffs.append(np.mean(diff_matrix))

        fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

        axs[0].plot(range(T), std_devs, color="blue", lw=2)
        axs[0].set_ylabel("Std Dev", fontsize=12)
        axs[0].grid(True)
        axs[0].set_title(descr)

        axs[1].plot(range(T), entropies, color="green", lw=2)
        axs[1].set_ylabel("Entropy", fontsize=12)
        axs[1].grid(True)

        axs[2].plot(range(T), mean_pairwise_diffs, color="orange", lw=2)
        axs[2].set_ylabel("Mean Pairwise Diff", fontsize=12)
        axs[2].set_xlabel("Iterations", fontsize=12)
        axs[2].grid(True)

        plt.tight_layout()

        if filename is not None:
            plt.savefig(filename)
            plt.clf()
        else:
            plt.show()
