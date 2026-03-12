import os
import matplotlib as mpl

if os.environ.get("DISPLAY", "") == "":
    mpl.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
import networkx as nx

__author__ = "Peter Carragher"
__license__ = "BSD-2-Clause"
__email__ = "petercarragher6@gmail.com"

# Categorical palette for discrete-state models (SIR-style)
_DISCRETE_PALETTE = [
    "#1f77b4",  # blue   – status 0 (Susceptible)
    "#d62728",  # red    – status 1 (Infected)
    "#2ca02c",  # green  – status 2 (Recovered)
    "#ff7f0e",  # orange
    "#9467bd",  # purple
    "#8c564b",  # brown
    "#e377c2",  # pink
    "#7f7f7f",  # grey
    "#bcbd22",  # yellow-green
    "#17becf",  # cyan
]


class DiffusionAnimator(object):
    def __init__(self, model, iterations, pos=None):
        """
        :param model: A configured and executed NDLib diffusion model.
        :param iterations: Output of ``model.iteration_bunch()``.
        :param pos: Optional dict mapping node id → (x, y).  If *None*,
                    a spring layout is computed automatically.
        """
        self.model = model
        self.iterations = iterations
        self.graph = model.graph.graph
        self.pos = pos if pos is not None else nx.spring_layout(self.graph)

        # Detect discrete (SIR-style) vs continuous (opinion) model.
        # Models with more than one named status are treated as discrete.
        statuses = model.available_statuses
        self._discrete = len(statuses) > 1

        if self._discrete:
            self._srev = {v: k for k, v in statuses.items()}
            unique_ids = sorted(statuses.values())
            self._status_color = {
                sid: _DISCRETE_PALETTE[i % len(_DISCRETE_PALETTE)]
                for i, sid in enumerate(unique_ids)
            }
        else:
            self._cmap = plt.cm.RdYlBu_r

        self._node_colors = self._build_node_colors()

    def _build_node_colors(self):
        """Return a list (one entry per iteration) of per-node colour arrays."""
        nodes = list(self.graph.nodes())
        current = {node: 0 for node in nodes}

        colors_per_iteration = []
        for it in self.iterations:
            current.update(it["status"])
            if self._discrete:
                frame = [
                    self._status_color.get(current[node], "#7f7f7f")
                    for node in nodes
                ]
            else:
                frame = [self._cmap(float(current[node])) for node in nodes]
            colors_per_iteration.append(frame)

        return colors_per_iteration

    def plot(self):
        """
        Build and return a :class:`matplotlib.animation.FuncAnimation` of the
        diffusion process over the graph.

        The returned object can be displayed inline in a Jupyter notebook or
        passed to :meth:`save_gif`.

        :return: :class:`matplotlib.animation.FuncAnimation`
        """
        fig, ax = plt.subplots()
        ax.axis("off")

        nodes_artist = nx.draw_networkx_nodes(
            self.graph, self.pos, node_color=self._node_colors[0], ax=ax
        )
        nx.draw_networkx_edges(self.graph, self.pos, ax=ax, alpha=0.3)

        if self._discrete:
            legend_elements = [
                Line2D(
                    [0], [0],
                    marker="o",
                    color="w",
                    markerfacecolor=self._status_color[sid],
                    markersize=10,
                    label=self._srev[sid],
                )
                for sid in sorted(self._status_color)
            ]
            ax.legend(handles=legend_elements, loc="upper right", fontsize=9)

        timestep_text = ax.text(
            0.05,
            0.95,
            "",
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        def _update(frame):
            nodes_artist.set_facecolor(self._node_colors[frame])
            timestep_text.set_text(
                "Iteration: {}".format(self.iterations[frame]["iteration"])
            )
            return (nodes_artist,)

        animation = FuncAnimation(
            fig,
            _update,
            frames=len(self._node_colors),
            interval=200,
            blit=True,
        )
        return animation

    def save_gif(self, filename, fps=10):
        """
        Save the animation as a GIF file.

        :param filename: Output path, e.g. ``"diffusion.gif"``.
        :param fps: Frames per second (default 10).
        """
        animation = self.plot()
        animation.save(
            filename,
            writer="pillow",
            fps=fps,
            savefig_kwargs={"facecolor": "white"},
        )
        animation.event_source.stop()
        plt.close("all")
