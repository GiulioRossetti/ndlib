import os
import matplotlib as mpl
if os.environ.get("DISPLAY", "") == "":
    mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import future.utils

__author__ = "Antigravity"
__license__ = "BSD-2-Clause"


class TransmissionTreeViz(object):
    def __init__(self, model, iterations, active_statuses=["Infected"], susceptible_status="Susceptible"):
        """
        :param model: The model object
        :param iterations: The computed simulation iterations (single run)
        :param active_statuses: List of status names representing active infection
        :param susceptible_status: Name of the susceptible status
        """
        self.model = model
        self.srev = iterations
        self.active_statuses = active_statuses
        self.susceptible_status = susceptible_status

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

        statuses = self.model.available_statuses
        active_codes = [statuses[name] for name in self.active_statuses if name in statuses]
        sus_code = statuses[self.susceptible_status]

        # Reconstruct node states at each step
        last_it = self.srev[-1]["iteration"] + 1
        node_states = {n: [sus_code] * last_it for n in self.model.graph.nodes}
        last_seen = {n: 0 for n in self.model.graph.nodes}

        for it in self.srev:
            sts = it["status"]
            its = it["iteration"]
            for n, v in sts.items():
                if n in node_states:
                    last_id = last_seen[n]
                    last_value = node_states[n][last_id]
                    for i in range(last_id, its):
                        node_states[n][i] = last_value
                    node_states[n][its] = v
                    last_seen[n] = its

        for n in node_states:
            last_id = last_seen[n]
            last_value = node_states[n][last_id]
            for i in range(last_id + 1, last_it):
                node_states[n][i] = last_value

        transmission_edges = []
        for t in range(1, last_it):
            for v in node_states:
                # If v transitioned to an active state at step t
                if node_states[v][t] in active_codes and node_states[v][t - 1] == sus_code:
                    if self.model.graph.directed:
                        candidates = list(self.model.graph.predecessors(v))
                    else:
                        candidates = list(self.model.graph.neighbors(v))

                    # Filter candidates that were active at t-1
                    infectors = [c for c in candidates if node_states[c][t - 1] in active_codes]
                    if infectors:
                        parent = np.random.choice(infectors)
                        transmission_edges.append((parent, v))

        # Build transmission graph to count out-degrees
        t_graph = nx.DiGraph()
        t_graph.add_nodes_from(self.model.graph.nodes)
        t_graph.add_edges_from(transmission_edges)

        out_degrees = [d for n, d in t_graph.out_degree()]
        max_deg = max(out_degrees) if out_degrees else 0

        plt.figure(figsize=(8, 6))
        # Plot secondary infection counts histogram
        counts, bins = np.histogram(out_degrees, bins=range(max_deg + 2))
        plt.bar(bins[:-1], counts, width=0.8, color="salmon", edgecolor="black", align="center")
        
        plt.title("Distribution of Secondary Infections\n%s" % descr, fontsize=12)
        plt.xlabel("Number of Secondary Infections (Individual R_i)", fontsize=12)
        plt.ylabel("Number of Nodes", fontsize=12)
        plt.xticks(range(max_deg + 1))
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()

        if filename is not None:
            plt.savefig(filename)
            plt.clf()
        else:
            plt.show()
