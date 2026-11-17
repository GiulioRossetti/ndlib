"""
Choose which nodes to seed or to immunize before running a diffusion model.

Every epidemic model takes its initial "Infected" (and, for SIR-like models,
"Removed") nodes from ``ModelConfig.add_model_initial_configuration``. This
module ranks nodes so those sets can be chosen by a structural rule instead of
at random::

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as ep
    from ndlib.node_selection import select_nodes

    g = nx.karate_club_graph()
    model = ep.SIRModel(g, seed=1)
    cfg = mc.Configuration()
    cfg.add_model_parameter("beta", 0.1)
    cfg.add_model_parameter("gamma", 0.2)
    cfg.add_model_parameter("fraction_infected", 0.05)
    cfg.add_model_initial_configuration("Removed", select_nodes(g, 3, "kcore"))
    model.set_initial_status(cfg)

Strategies:

* ``random``: a uniform sample, drawn with ``seed``.
* ``degree``, ``betweenness``, ``pagerank``: the usual centralities.
* ``kcore``: coreness, ties broken by degree (Kitsak et al., Nature Physics 6, 2010).
* ``collective_influence``: adaptive collective influence with ball radius
  ``ci_radius`` (default 2), recomputed after every removal (Morone and Makse,
  Nature 524, 2015). The reinsertion step of the paper is not applied.

The graph is treated as undirected and simple. Ties are broken by scores
rounded to 1e-9 and then by a permutation of the nodes drawn with
``tie_seed``, so results do not depend on floating-point noise.
"""

import random

import networkx as nx
import numpy as np

__all__ = ["STRATEGIES", "rank_nodes", "select_nodes"]

STRATEGIES = (
    "random",
    "degree",
    "betweenness",
    "pagerank",
    "kcore",
    "collective_influence",
)


def _simple_undirected(graph):
    g = nx.Graph(graph)
    g.remove_edges_from(list(nx.selfloop_edges(g)))
    return g


def _order(nodes, scores, tie_seed):
    """Nodes sorted by score (high first), ties broken by a seeded permutation."""
    perm = list(nodes)
    random.Random(tie_seed).shuffle(perm)
    tie_rank = {n: i for i, n in enumerate(perm)}
    return sorted(nodes, key=lambda n: (-round(float(scores[n]), 9), tie_rank[n]))


def _collective_influence_order(g, k, radius, tie_seed):
    """Adaptive CI: remove the top node, recompute, repeat k times."""
    nodes = list(g)
    index = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    rows, cols = [], []
    for u, v in g.edges():
        rows += [index[u], index[v]]
        cols += [index[v], index[u]]
    import scipy.sparse as sp

    adj0 = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    perm = list(range(n))
    random.Random(tie_seed).shuffle(perm)
    tie_rank = np.empty(n)
    tie_rank[perm] = np.arange(n)
    alive = np.ones(n, dtype=bool)
    order = []
    for _ in range(k):
        mask = sp.diags(alive.astype(float))
        adj = (mask @ adj0 @ mask).tocsr()
        adj.eliminate_zeros()
        deg = np.asarray(adj.sum(axis=1)).ravel()
        excess = np.clip(deg - 1.0, 0.0, None)
        # nodes at distance exactly `radius`: reachable in `radius` steps but not fewer
        reach = sp.identity(n, format="csr")
        seen = reach.copy()
        frontier = reach
        for _r in range(radius):
            step = (frontier @ adj).astype(bool).astype(float)
            frontier = (step - step.multiply(seen.astype(bool))).tocsr()
            frontier.eliminate_zeros()
            seen = (seen + frontier).astype(bool).astype(float)
        ci = excess * np.asarray(frontier @ excess).ravel()
        ci = np.round(ci, 9)
        ci[~alive] = -1.0
        best = ci.max()
        cand = np.flatnonzero(ci == best)
        pick = int(cand[np.argmin(tie_rank[cand])])
        order.append(nodes[pick])
        alive[pick] = False
    return order


def rank_nodes(graph, strategy="degree", k=None, seed=None, tie_seed=0, ci_radius=2):
    """Nodes ordered from most to least preferred under ``strategy``.

    For ``collective_influence`` only the first ``k`` nodes are computed
    (the order is adaptive); for the other strategies ``k`` is ignored.
    """
    if strategy not in STRATEGIES:
        raise ValueError("unknown strategy %r; choose one of %s" % (strategy, ", ".join(STRATEGIES)))
    g = _simple_undirected(graph)
    nodes = list(g)
    if strategy == "random":
        out = list(nodes)
        random.Random(seed).shuffle(out)
        return out
    if strategy == "collective_influence":
        return _collective_influence_order(g, len(nodes) if k is None else k, ci_radius, tie_seed)
    if strategy == "degree":
        scores = dict(g.degree())
    elif strategy == "betweenness":
        scores = nx.betweenness_centrality(g)
    elif strategy == "pagerank":
        scores = nx.pagerank(g, alpha=0.85)
    elif strategy == "kcore":
        core = nx.core_number(g)
        kmax = max((d for _, d in g.degree()), default=0) + 1
        scores = {n: core[n] + g.degree(n) / kmax for n in g}
    return _order(nodes, scores, tie_seed)


def select_nodes(graph, k, strategy="degree", seed=None, **kwargs):
    """The top ``k`` nodes under ``strategy`` (see :func:`rank_nodes`)."""
    n = graph.number_of_nodes()
    if not 0 <= k <= n:
        raise ValueError("k must be between 0 and the number of nodes (%d)" % n)
    if k == 0:
        return []
    return rank_nodes(graph, strategy, k=k, seed=seed, **kwargs)[:k]
