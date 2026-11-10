from ndlib.models.DiffusionModel import DiffusionModel
import future.utils
import numpy as np
from ndlib.models.opinions.initial_opinion_distribution import sample_initial_opinions

__author__ = ["Pau Maynou"]
__license__ = "BSD-2-Clause"


class DeffuantModel(DiffusionModel):
    """
    Deffuant-Weisbuch model of continuous opinion dynamics.

    In each iteration, N pairwise interactions are drawn uniformly at random
    from the edge set.  Two agents i and j update their opinions only when
    their current opinions lie within the bounded-confidence threshold epsilon:

        if |x_i - x_j| <= epsilon:
            x_i <- x_i + mu * (x_j - x_i)
            x_j <- x_j + mu * (x_i - x_j)   # uses the *old* x_i

    The convergence parameter mu controls how far each agent moves toward its
    partner in a single step (mu = 0.5 corresponds to full averaging).

    Depending on epsilon, the system converges to either full consensus
    (large epsilon) or fragmented opinion clusters (small epsilon), making
    it a canonical model for studying polarisation on networks.

    Model Parameters to be specified via ModelConfig:

    :param epsilon: bounded-confidence threshold in [0, 1] (required)
    :param mu: convergence / cautiousness rate in (0, 0.5] (optional, default 0.5)
    :param initial_opinion_distribution: initial distribution of opinions (optional, default "uniform")

    Reference:
        Deffuant, G., Neau, D., Amblard, F., & Weisbuch, G. (2000).
        Mixing beliefs among interacting agents.
        Advances in Complex Systems, 3(1-4), 87-98.
        https://doi.org/10.1142/S0219525900000078
    """

    def __init__(self, graph, seed=None):
        """
        Model Constructor

        :param graph: A networkx graph object
        :param seed: Random seed for reproducibility (optional)
        """
        super(self.__class__, self).__init__(graph, seed)
        self.discrete_state = False

        self.available_statuses = {"Infected": 0}

        self.parameters = {
            "model": {
                "epsilon": {
                    "descr": "Bounded confidence threshold",
                    "range": [0, 1],
                    "optional": False,
                },
                "mu": {
                    "descr": "Convergence/cautiousness parameter",
                    "range": [0, 0.5],
                    "optional": True,
                    "default": 0.5,
                },
                "initial_opinion_distribution": {
                    "descr": "Initial opinion distribution in [0, 1]",
                    "choices": [
                        {"value": "uniform", "label": "Uniform"},
                        {"value": "normal", "label": "Normal"},
                        {"value": "gaussian", "label": "Gaussian"},
                        {"value": "bimodal", "label": "Bimodal"},
                        {"value": "left_skewed", "label": "Left skewed"},
                        {"value": "right_skewed", "label": "Right skewed"},
                        {"value": "polarized", "label": "Polarized"},
                    ],
                    "optional": True,
                    "default": "uniform",
                },
            },
            "edges": {},
            "nodes": {},
        }
        self.name = "Deffuant"

    def set_initial_status(self, configuration=None):
        """
        Override behaviour of methods in class DiffusionModel.
        Assigns each node a continuous opinion drawn from the chosen distribution.
        """
        super(DeffuantModel, self).set_initial_status(configuration)

        opinions = sample_initial_opinions(
            len(self.status),
            self.params["model"].get("initial_opinion_distribution", "uniform"),
        )
        for node, opinion in zip(self.status, opinions):
            self.status[node] = float(opinion)
        self.initial_status = self.status.copy()

    def clean_initial_status(self, valid_status=None):
        for n, s in future.utils.iteritems(self.status):
            if s > 1 or s < 0:
                self.status[n] = 0.5

    def iteration(self, node_status=True):
        """
        Execute a single model iteration.

        Each iteration samples N random edges (where N is the number of nodes)
        and applies the Deffuant pairwise update rule to each selected pair.

        :return: dict with keys 'iteration', 'status', 'node_count', 'status_delta'
        """
        self.clean_initial_status(None)

        actual_status = {
            node: nstatus for node, nstatus in future.utils.iteritems(self.status)
        }

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(self.status)
            if node_status:
                return {
                    "iteration": 0,
                    "status": self.status.copy(),
                    "node_count": node_count.copy(),
                    "status_delta": status_delta.copy(),
                }
            else:
                return {
                    "iteration": 0,
                    "status": {},
                    "node_count": node_count.copy(),
                    "status_delta": status_delta.copy(),
                }

        edges = list(self.graph.edges)
        if len(edges) == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(actual_status)
            self.status = actual_status
            return {
                "iteration": self.actual_iteration - 1,
                "status": delta.copy() if node_status else {},
                "node_count": node_count.copy(),
                "status_delta": status_delta.copy(),
            }

        epsilon = self.params["model"]["epsilon"]
        mu = self.params["model"].get("mu", 0.5)

        # Perform N pairwise interactions (one per node on average)
        n_interactions = self.graph.number_of_nodes()
        for _ in range(n_interactions):
            edge = edges[np.random.randint(0, len(edges))]
            i, j = edge

            xi = actual_status[i]
            xj = actual_status[j]

            if abs(xi - xj) <= epsilon:
                # Both agents move toward each other by rate mu
                actual_status[i] = xi + mu * (xj - xi)
                actual_status[j] = xj + mu * (xi - xj)  # uses old xi

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {
                "iteration": self.actual_iteration - 1,
                "status": delta.copy(),
                "node_count": node_count.copy(),
                "status_delta": status_delta.copy(),
            }
        else:
            return {
                "iteration": self.actual_iteration - 1,
                "status": {},
                "node_count": node_count.copy(),
                "status_delta": status_delta.copy(),
            }
