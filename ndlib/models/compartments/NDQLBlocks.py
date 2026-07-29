import math
import random
import statistics

import networkx as nx
import numpy as np

from ndlib.models.compartments.Compartment import Compartiment, ConfigurationException
from ndlib.models.compartments.ConditionalComposition import ConditionalComposition
from ndlib.models.opinions.initial_opinion_distribution import sample_initial_opinions

__author__ = "Antigravity"
__license__ = "BSD-2-Clause"


def _coerce_number(value, fallback=0.0):
    try:
        if isinstance(value, bool):
            return float(fallback)
        if isinstance(value, (int, float, np.integer, np.floating)):
            return float(value)
        text = str(value).strip()
        if not text:
            return float(fallback)
        return float(text)
    except (TypeError, ValueError):
        return float(fallback)


def _clamp(value, minimum=0.0, maximum=1.0):
    minimum = float(minimum)
    maximum = float(maximum)
    if maximum < minimum:
        minimum, maximum = maximum, minimum
    return float(min(max(_coerce_number(value, minimum), minimum), maximum))


def _safe_eval(expression, context, default=None):
    if expression is None or expression == "":
        return default
    namespace = {
        "__builtins__": {},
        "abs": abs,
        "min": min,
        "max": max,
        "sum": sum,
        "len": len,
        "sorted": sorted,
        "round": round,
        "math": math,
        "np": np,
    }
    try:
        return eval(str(expression), namespace, context)
    except Exception:
        return default


def _node_context(node, graph, status, params=None):
    params = params or {}
    model_params = params.get("model", {}) if isinstance(params, dict) else {}
    try:
        node_attrs = dict(graph.nodes[node])
    except Exception:
        node_attrs = {}
    neighbors = list(graph.neighbors(node))
    if hasattr(graph, "is_directed") and graph.is_directed():
        neighbors = list(graph.predecessors(node))
    neighbor_statuses = [status[n] for n in neighbors if n in status]
    numeric_neighbor_statuses = []
    for value in neighbor_statuses:
        try:
            numeric_neighbor_statuses.append(float(value))
        except (TypeError, ValueError):
            continue
    opinion = node_attrs.get("opinion")
    if opinion is None and node in status:
        opinion = status[node]
    try:
        opinion = float(opinion) if opinion is not None else None
    except (TypeError, ValueError):
        pass
    context = {
        "node": node,
        "graph": graph,
        "status": status,
        "params": params,
        "model": model_params,
        "attrs": node_attrs,
        "neighbors": neighbors,
        "neighbor_statuses": neighbor_statuses,
        "neighbor_values": neighbor_statuses,
        "neighbor_mean": float(np.mean(numeric_neighbor_statuses)) if numeric_neighbor_statuses else 0.0,
        "neighbor_median": float(statistics.median(numeric_neighbor_statuses)) if numeric_neighbor_statuses else 0.0,
        "neighbor_min": float(min(numeric_neighbor_statuses)) if numeric_neighbor_statuses else 0.0,
        "neighbor_max": float(max(numeric_neighbor_statuses)) if numeric_neighbor_statuses else 0.0,
        "degree": graph.degree(node) if hasattr(graph, "degree") else 0,
        "opinion": opinion,
        "value": opinion if opinion is not None else status.get(node),
        "np": np,
        "math": math,
    }
    context.update(node_attrs)
    return context


def _get_opinion_value(graph, status, node, fallback=0.0):
    try:
        graph_value = graph.nodes[node].get("opinion")
        if graph_value is not None:
            return float(graph_value)
    except (TypeError, ValueError):
        pass
    except Exception:
        pass
    value = status.get(node, fallback)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(fallback)


def _set_opinion_value(graph, status, node, value, topic=None):
    if topic is None:
        try:
            graph.nodes[node]["opinion"] = float(value)
        except Exception:
            pass
        if node in status:
            current_status = status.get(node)
            if isinstance(current_status, (float, np.floating)):
                status[node] = float(value)
        return
    try:
        graph.nodes[node][topic] = float(value)
    except Exception:
        pass


def _coerce_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def _status_matches(node_status, filter_values, labels=None):
    if filter_values is None:
        return True
    candidates = _coerce_list(filter_values)
    if not candidates:
        return True
    label = None
    if isinstance(labels, dict):
        for key, value in labels.items():
            if value == node_status:
                label = key
                break
    for candidate in candidates:
        if candidate == node_status:
            return True
        try:
            if float(candidate) == float(node_status):
                return True
        except (TypeError, ValueError):
            pass
        if label is not None and str(candidate) == str(label):
            return True
    return False


def _graph_iteration(params=None):
    if isinstance(params, dict):
        return int(params.get("model", {}).get("iteration", params.get("iteration", 0)) or 0)
    return 0


def _iter_neighbors(graph, node):
    if hasattr(graph, "is_directed") and graph.is_directed():
        return list(graph.predecessors(node))
    return list(graph.neighbors(node))


def _random_node(graph, exclude=None):
    nodes = list(graph.nodes())
    if exclude is not None:
        exclude = set(exclude)
        nodes = [n for n in nodes if n not in exclude]
    if not nodes:
        return None
    return nodes[np.random.randint(0, len(nodes))]


def _sample_bool(probability):
    probability = _clamp(probability, 0.0, 1.0)
    return bool(np.random.random_sample() <= probability)


class NDQLBlockBase(Compartiment):
    def __init__(self, block_type=None, params=None, **kwargs):
        super(NDQLBlockBase, self).__init__(kwargs)
        self.block_type = block_type
        self.params = params or {}

    def execute(self, *args, **kwargs):
        return self.compose(*args, **kwargs)


class Parameter(NDQLBlockBase):
    def __init__(
        self,
        name=None,
        value=None,
        type=None,
        default=None,
        range=None,
        choices=None,
        scope=None,
        optional=True,
        **kwargs
    ):
        super(Parameter, self).__init__(kwargs)
        self.name = name
        self.value = value if value is not None else default
        self.type = type
        self.default = default
        self.range = range
        self.choices = choices
        self.scope = scope
        self.optional = optional

    def resolve(self, fallback=None):
        if self.value is not None:
            return self.value
        if self.default is not None:
            return self.default
        return fallback


class Constant(NDQLBlockBase):
    def __init__(self, name=None, value=None, type=None, **kwargs):
        super(Constant, self).__init__(kwargs)
        self.name = name
        self.value = value
        self.type = type

    def resolve(self):
        return self.value


class Variable(NDQLBlockBase):
    def __init__(
        self,
        name=None,
        scope="node",
        type=None,
        range=None,
        default=None,
        values=None,
        **kwargs
    ):
        super(Variable, self).__init__(kwargs)
        self.name = name
        self.scope = scope
        self.type = type
        self.range = range
        self.default = default
        self.values = values


class Distribution(NDQLBlockBase):
    def __init__(self, family="uniform", params=None, bounds=None, name=None, **kwargs):
        super(Distribution, self).__init__(kwargs)
        self.family = str(family or "uniform").lower()
        self.params = params or {}
        self.bounds = bounds if bounds is not None else [0.0, 1.0]
        self.name = name

    def sample(self, size=1):
        size = int(max(1, size))
        bounds = list(self.bounds) if isinstance(self.bounds, (list, tuple)) and len(self.bounds) >= 2 else [0.0, 1.0]
        low = float(bounds[0])
        high = float(bounds[1])
        if high < low:
            low, high = high, low

        if self.family in {"normal", "gaussian"}:
            mu = _coerce_number(self.params.get("mean", self.params.get("mu", 0.5)), 0.5)
            sigma = abs(_coerce_number(self.params.get("sigma", 0.15), 0.15))
            values = np.random.normal(mu, sigma, size=size)
        elif self.family == "bimodal":
            low_mu = _coerce_number(self.params.get("low", 0.25), 0.25)
            high_mu = _coerce_number(self.params.get("high", 0.75), 0.75)
            sigma = abs(_coerce_number(self.params.get("sigma", 0.08), 0.08))
            mask = np.random.random_sample(size) < float(self.params.get("mix", 0.5))
            values = np.empty(size, dtype=float)
            low_count = int(mask.sum())
            high_count = size - low_count
            values[mask] = np.random.normal(low_mu, sigma, size=low_count)
            values[~mask] = np.random.normal(high_mu, sigma, size=high_count)
        elif self.family in {"beta", "polarized"}:
            a = _coerce_number(self.params.get("alpha", 2.0), 2.0)
            b = _coerce_number(self.params.get("beta", 2.0), 2.0)
            values = np.random.beta(max(a, 1e-3), max(b, 1e-3), size=size)
        elif self.family in {"left_skewed", "left-skewed", "skewed_left"}:
            values = np.random.beta(2.0, 5.0, size=size)
        elif self.family in {"right_skewed", "right-skewed", "skewed_right"}:
            values = np.random.beta(5.0, 2.0, size=size)
        elif self.family in {"triangular", "triangle"}:
            mode = _coerce_number(self.params.get("mode", 0.5), 0.5)
            values = np.random.triangular(low, mode, high, size=size)
        else:
            values = np.random.random_sample(size)

        return np.clip(values, low, high)

    def execute(self, *args, **kwargs):
        return self.compose(*args, **kwargs)


class Compose(ConditionalComposition):
    def __init__(
        self,
        condition=None,
        if_true=None,
        if_false=None,
        first_branch=None,
        second_branch=None,
        **kwargs
    ):
        true_branch = if_true if if_true is not None else first_branch
        false_branch = if_false if if_false is not None else second_branch
        ConditionalComposition.__init__(self, condition, true_branch, false_branch, **kwargs)


class Filter(NDQLBlockBase):
    def __init__(self, predicate=None, expression=None, threshold=None, **kwargs):
        super(Filter, self).__init__(kwargs)
        self.predicate = predicate if predicate is not None else expression
        self.threshold = threshold

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        context = _node_context(node, graph, status, params)
        if self.predicate is None and self.threshold is not None:
            test = float(context.get("value") or 0.0) >= _coerce_number(self.threshold, 0.0)
        else:
            test = bool(_safe_eval(self.predicate, context, default=False))
        if test:
            return self.compose(node, graph, status, status_map, params, kwargs)
        return False


class Selector(NDQLBlockBase):
    def __init__(self, policy="random", share=None, predicate=None, bias=None, **kwargs):
        super(Selector, self).__init__(kwargs)
        self.policy = str(policy or "random").lower()
        self.share = share
        self.predicate = predicate
        self.bias = bias

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        context = _node_context(node, graph, status, params)
        selected = False
        if self.predicate is not None:
            selected = bool(_safe_eval(self.predicate, context, default=False))
        elif self.share is not None:
            selected = np.random.random_sample() <= float(self.share)
        elif self.policy == "highest":
            selected = float(context.get("value") or 0.0) >= float(context.get("neighbor_max") or 0.0)
        elif self.policy == "lowest":
            selected = float(context.get("value") or 0.0) <= float(context.get("neighbor_min") or 0.0)
        else:
            selected = True

        if selected and self.bias is not None:
            selected = bool(_safe_eval(self.bias, context, default=True))

        if selected:
            return self.compose(node, graph, status, status_map, params, kwargs)
        return False


class Aggregator(NDQLBlockBase):
    def __init__(self, mode="mean", attribute=None, variable=None, target=None, **kwargs):
        super(Aggregator, self).__init__(kwargs)
        self.mode = str(mode or "mean").lower()
        self.attribute = attribute
        self.variable = variable
        self.target = target
        self.last_value = None

    def _values(self, node, graph, status, params=None):
        context = _node_context(node, graph, status, params)
        neighbors = context["neighbors"]
        if self.attribute is not None:
            values = [graph.nodes[n].get(self.attribute) for n in neighbors if self.attribute in graph.nodes[n]]
        elif self.variable is not None:
            values = [context.get(self.variable)]
            if self.variable in status:
                values = [status[n] for n in neighbors if n in status]
        else:
            values = [status[n] for n in neighbors if n in status]
        numeric_values = []
        for value in values:
            try:
                numeric_values.append(float(value))
            except (TypeError, ValueError):
                continue
        return numeric_values, context

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        values, context = self._values(node, graph, status, params)
        if not values:
            agg = 0.0
        elif self.mode in {"mean", "avg", "average"}:
            agg = float(np.mean(values))
        elif self.mode == "median":
            agg = float(statistics.median(values))
        elif self.mode == "min":
            agg = float(min(values))
        elif self.mode == "max":
            agg = float(max(values))
        elif self.mode == "sum":
            agg = float(np.sum(values))
        elif self.mode in {"count", "size"}:
            agg = float(len(values))
        elif self.mode == "majority":
            uniques, counts = np.unique(values, return_counts=True)
            agg = float(uniques[np.argmax(counts)])
        else:
            agg = float(np.mean(values))
        self.last_value = agg
        if self.target:
            if node in graph:
                graph.nodes[node][self.target] = agg
        context[self.target or "aggregate"] = agg
        return self.compose(node, graph, status, status_map, params, kwargs)


class Kernel(NDQLBlockBase):
    def __init__(self, formula=None, expression=None, rate=None, step=None, clamp=True, **kwargs):
        super(Kernel, self).__init__(kwargs)
        self.formula = formula if formula is not None else expression
        self.rate = rate
        self.step = step
        self.clamp = clamp

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        context = _node_context(node, graph, status, params)
        probability = self.rate
        if probability is None:
            probability = self.step
        if probability is None and self.formula is not None:
            probability = _safe_eval(self.formula, context, default=0.0)
        probability = _coerce_number(probability, 0.0)
        if self.clamp:
            probability = _clamp(probability, 0.0, 1.0)
        if np.random.random_sample() <= probability:
            return self.compose(node, graph, status, status_map, params, kwargs)
        return False


class Transform(NDQLBlockBase):
    def __init__(self, expression=None, target=None, clamp=None, source=None, **kwargs):
        super(Transform, self).__init__(kwargs)
        self.expression = expression
        self.target = target
        self.clamp = clamp
        self.source = source

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        context = _node_context(node, graph, status, params)
        if self.source is not None:
            context["source"] = context.get(self.source, status.get(node))
        value = _safe_eval(self.expression, context, default=context.get("value"))
        if value is None:
            value = context.get("value")
        if self.clamp is not None:
            if isinstance(self.clamp, (list, tuple)) and len(self.clamp) >= 2:
                value = _clamp(value, self.clamp[0], self.clamp[1])
            elif bool(self.clamp):
                value = _clamp(value, 0.0, 1.0)
        if self.target:
            if self.target in {"status", "state"}:
                status[node] = value
            else:
                graph.nodes[node][self.target] = value
        else:
            try:
                graph.nodes[node]["value"] = value
            except Exception:
                pass
        return self.compose(node, graph, status, status_map, params, kwargs)


class ClampNormalize(NDQLBlockBase):
    def __init__(self, min=0.0, max=1.0, renormalize=False, target="opinion", **kwargs):
        super(ClampNormalize, self).__init__(kwargs)
        self.minimum = _coerce_number(min, 0.0)
        self.maximum = _coerce_number(max, 1.0)
        self.renormalize = bool(renormalize)
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        if self.target in {"status", "state"}:
            value = status.get(node)
            if self.renormalize and self.maximum > self.minimum:
                value = (float(value) - self.minimum) / (self.maximum - self.minimum)
            status[node] = _clamp(value, self.minimum, self.maximum)
        else:
            value = graph.nodes[node].get(self.target)
            if self.renormalize and self.maximum > self.minimum:
                value = (float(value) - self.minimum) / (self.maximum - self.minimum)
            graph.nodes[node][self.target] = _clamp(value, self.minimum, self.maximum)
        return self.compose(node, graph, status, status_map, params, kwargs)


class Schedule(NDQLBlockBase):
    def __init__(self, start=0, end=None, period=None, phase=0, **kwargs):
        super(Schedule, self).__init__(kwargs)
        self.start = int(start or 0)
        self.end = None if end is None or end == "" else int(end)
        self.period = None if period is None or period == "" else max(1, int(period))
        self.phase = int(phase or 0)

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        iteration = 0
        if isinstance(params, dict):
            iteration = int(params.get("model", {}).get("iteration", params.get("iteration", 0)) or 0)
        active = iteration >= self.start
        if active and self.end is not None:
            active = iteration <= self.end
        if active and self.period is not None:
            active = ((iteration - self.phase) % self.period) == 0
        if active:
            return self.compose(node, graph, status, status_map, params, kwargs)
        return False


class Observe(NDQLBlockBase):
    def __init__(self, variable=None, mode="value", bins=None, range=None, **kwargs):
        super(Observe, self).__init__(kwargs)
        self.variable = variable
        self.mode = mode
        self.bins = bins
        self.range = range

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        if not hasattr(graph, "graph"):
            return self.compose(node, graph, status, status_map, params, kwargs)
        observations = graph.graph.setdefault("_ndql_observations", [])
        context = _node_context(node, graph, status, params)
        value = context.get(self.variable, context.get("value"))
        observations.append(
            {
                "node": node,
                "variable": self.variable,
                "mode": self.mode,
                "bins": self.bins,
                "range": self.range,
                "value": value,
            }
        )
        return self.compose(node, graph, status, status_map, params, kwargs)


class OpinionDistribution(Distribution):
    def __init__(self, family="uniform", params=None, bounds=None, **kwargs):
        super(OpinionDistribution, self).__init__(family=family, params=params, bounds=bounds, **kwargs)

    def sample(self, size=1):
        return sample_initial_opinions(size, {"family": self.family, "params": self.params, "bounds": self.bounds})


class OpinionStubbornness(NDQLBlockBase):
    def __init__(self, theta=0.1, floor=0.0, **kwargs):
        super(OpinionStubbornness, self).__init__(kwargs)
        self.theta = _clamp(theta, 0.0, 1.0)
        self.floor = _clamp(floor, 0.0, 1.0)

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        initial_map = {}
        if isinstance(params, dict):
            initial_map = params.get("model", {}).get("initial_opinion_map", {}) or {}
        baseline = initial_map.get(node, _get_opinion_value(graph, status, node))
        current = _get_opinion_value(graph, status, node)
        new_value = (1.0 - self.theta) * current + self.theta * _coerce_number(baseline, current)
        new_value = _clamp(new_value, self.floor, 1.0)
        _set_opinion_value(graph, status, node, new_value)
        return self.compose(node, graph, status, status_map, params, kwargs)


class OpinionNoise(NDQLBlockBase):
    def __init__(self, sigma=0.0, distribution="gaussian", **kwargs):
        super(OpinionNoise, self).__init__(kwargs)
        self.sigma = max(0.0, _coerce_number(sigma, 0.0))
        self.distribution = str(distribution or "gaussian").lower()

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        current = _get_opinion_value(graph, status, node)
        if self.sigma > 0.0:
            if self.distribution in {"uniform", "u"}:
                noise = np.random.uniform(-self.sigma, self.sigma)
            else:
                noise = np.random.normal(0.0, self.sigma)
            current = current + noise
        current = _clamp(current, 0.0, 1.0)
        _set_opinion_value(graph, status, node, current)
        return self.compose(node, graph, status, status_map, params, kwargs)


class OpinionPolarization(NDQLBlockBase):
    def __init__(self, strength=0.0, attractor_points=None, **kwargs):
        super(OpinionPolarization, self).__init__(kwargs)
        self.strength = _clamp(strength, 0.0, 1.0)
        self.attractor_points = attractor_points or [0.0, 1.0]

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        current = _get_opinion_value(graph, status, node)
        if current >= 0.5:
            current = current + self.strength * (1.0 - current)
        else:
            current = current - self.strength * current
        current = _clamp(current, 0.0, 1.0)
        _set_opinion_value(graph, status, node, current)
        return self.compose(node, graph, status, status_map, params, kwargs)


class OpinionMediaInfluence(NDQLBlockBase):
    def __init__(self, k=1, media_opinions=None, weights=None, weight=None, **kwargs):
        super(OpinionMediaInfluence, self).__init__(kwargs)
        self.k = max(1, int(round(_coerce_number(k, 1))))
        self.media_opinions = media_opinions or []
        self.weights = weights
        self.weight = _clamp(weight if weight is not None else 0.5, 0.0, 1.0)

    def _media_values(self, params=None):
        media = self.media_opinions
        if isinstance(params, dict):
            media = params.get("model", {}).get("media_opinions", media)
        if isinstance(media, (list, tuple, np.ndarray)) and len(media) > 0:
            arr = np.clip(np.asarray(media, dtype=float), 0.0, 1.0)
            if len(arr) < self.k:
                pad_value = float(arr[-1]) if len(arr) > 0 else 0.5
                arr = np.pad(arr, (0, self.k - len(arr)), mode="constant", constant_values=pad_value)
            return arr[: self.k]
        return np.full(self.k, 0.5, dtype=float)

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        current = _get_opinion_value(graph, status, node)
        media_vals = self._media_values(params)
        target = float(np.mean(media_vals))
        current = _clamp((1.0 - self.weight) * current + self.weight * target, 0.0, 1.0)
        _set_opinion_value(graph, status, node, current)
        return self.compose(node, graph, status, status_map, params, kwargs)


class OpinionTrustFilter(NDQLBlockBase):
    def __init__(self, trust_threshold=0.1, signed=False, asymmetry=1.0, **kwargs):
        super(OpinionTrustFilter, self).__init__(kwargs)
        self.trust_threshold = _clamp(trust_threshold, 0.0, 1.0)
        self.signed = bool(signed)
        self.asymmetry = _coerce_number(asymmetry, 1.0)

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        context = _node_context(node, graph, status, params)
        threshold = self.trust_threshold
        if self.signed and context["neighbor_statuses"]:
            threshold *= max(0.0, self.asymmetry)
        current = float(context.get("value") or 0.0)
        if abs(current - context["neighbor_mean"]) <= threshold:
            return self.compose(node, graph, status, status_map, params, kwargs)
        return False


class OpinionConsensusBlock(NDQLBlockBase):
    def __init__(self, mode="mean", weights=None, confidence=None, target="opinion", **kwargs):
        super(OpinionConsensusBlock, self).__init__(kwargs)
        self.mode = str(mode or "mean").lower()
        self.weights = weights
        self.confidence = confidence
        self.target = target
        self.last_value = None

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        context = _node_context(node, graph, status, params)
        values = context["neighbor_statuses"]
        numeric = []
        for value in values:
            try:
                numeric.append(float(value))
            except (TypeError, ValueError):
                continue
        if not numeric:
            consensus = context.get("value")
            if consensus is None:
                return False
        elif self.mode in {"median"}:
            consensus = float(statistics.median(numeric))
        elif self.mode in {"majority"}:
            uniques, counts = np.unique(np.asarray(numeric), return_counts=True)
            consensus = float(uniques[np.argmax(counts)])
        elif self.mode in {"min"}:
            consensus = float(min(numeric))
        elif self.mode in {"max"}:
            consensus = float(max(numeric))
        else:
            consensus = float(np.mean(numeric))
        self.last_value = consensus
        if self.target in {"opinion", "value", "status"}:
            _set_opinion_value(graph, status, node, _clamp(consensus, 0.0, 1.0))
        else:
            try:
                graph.nodes[node][self.target] = consensus
            except Exception:
                pass
        return self.compose(node, graph, status, status_map, params, kwargs)


class OpinionRepulsion(NDQLBlockBase):
    def __init__(self, epsilon=0.1, strength=0.1, **kwargs):
        super(OpinionRepulsion, self).__init__(kwargs)
        self.epsilon = _clamp(epsilon, 0.0, 1.0)
        self.strength = _clamp(strength, 0.0, 1.0)

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        context = _node_context(node, graph, status, params)
        current = _coerce_number(context.get("value"), 0.0)
        neighbor_mean = context["neighbor_mean"]
        if abs(current - neighbor_mean) > self.epsilon:
            if current >= neighbor_mean:
                current = current + self.strength * (1.0 - current)
            else:
                current = current - self.strength * current
            _set_opinion_value(graph, status, node, _clamp(current, 0.0, 1.0))
            return self.compose(node, graph, status, status_map, params, kwargs)
        return False


class OpinionAssimilation(NDQLBlockBase):
    def __init__(self, rate=0.5, window=None, **kwargs):
        super(OpinionAssimilation, self).__init__(kwargs)
        self.rate = _clamp(rate, 0.0, 1.0)
        self.window = window

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        context = _node_context(node, graph, status, params)
        current = _coerce_number(context.get("value"), 0.0)
        target = context["neighbor_mean"]
        current = _clamp((1.0 - self.rate) * current + self.rate * target, 0.0, 1.0)
        _set_opinion_value(graph, status, node, current)
        return self.compose(node, graph, status, status_map, params, kwargs)


class OpinionExternalField(NDQLBlockBase):
    def __init__(self, target=0.5, strength=0.0, schedule=None, **kwargs):
        super(OpinionExternalField, self).__init__(kwargs)
        self.target = _clamp(target, 0.0, 1.0)
        self.strength = _clamp(strength, 0.0, 1.0)
        self.schedule = schedule

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        current = _get_opinion_value(graph, status, node)
        current = _clamp(current + self.strength * (self.target - current), 0.0, 1.0)
        _set_opinion_value(graph, status, node, current)
        return self.compose(node, graph, status, status_map, params, kwargs)


class OpinionMultiTopic(NDQLBlockBase):
    def __init__(self, topics=None, coupling=None, correlation=None, **kwargs):
        super(OpinionMultiTopic, self).__init__(kwargs)
        self.topics = list(topics or [])
        self.coupling = coupling if coupling is not None else 0.0
        self.correlation = correlation if correlation is not None else 0.0

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        if not self.topics:
            return self.compose(node, graph, status, status_map, params, kwargs)
        context = _node_context(node, graph, status, params)
        topic_values = []
        for topic in self.topics:
            try:
                value = float(graph.nodes[node].get(topic, context.get("value", 0.0)))
            except (TypeError, ValueError):
                value = float(context.get("value", 0.0))
            neighbors = context["neighbors"]
            neigh_vals = []
            for neigh in neighbors:
                try:
                    neigh_vals.append(float(graph.nodes[neigh].get(topic, value)))
                except (TypeError, ValueError):
                    continue
            if neigh_vals:
                value = (1.0 - self.coupling) * value + self.coupling * float(np.mean(neigh_vals))
            topic_values.append(_clamp(value, 0.0, 1.0))
        graph.nodes[node]["opinion_vector"] = topic_values
        for topic, value in zip(self.topics, topic_values):
            graph.nodes[node][topic] = float(value)
        return self.compose(node, graph, status, status_map, params, kwargs)


class OpinionLabelSwitch(NDQLBlockBase):
    def __init__(self, labels=None, probability=1.0, triggering_status=None, target=None, **kwargs):
        super(OpinionLabelSwitch, self).__init__(kwargs)
        self.labels = list(labels or [])
        self.probability = _clamp(probability, 0.0, 1.0)
        self.triggering_status = triggering_status
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        if self.triggering_status is not None:
            current = status.get(node)
            if isinstance(self.triggering_status, str):
                if current != status_map.get(self.triggering_status, current):
                    return False
            elif current != self.triggering_status:
                return False
        if self.labels:
            current = status.get(node)
            if current not in self.labels and str(current) not in {str(x) for x in self.labels}:
                return False
        if random.random() <= self.probability:
            return self.compose(node, graph, status, status_map, params, kwargs)
        return False


class OpinionBoundedDrift(NDQLBlockBase):
    def __init__(self, step=0.1, bounds=None, noise=0.0, **kwargs):
        super(OpinionBoundedDrift, self).__init__(kwargs)
        self.step = _clamp(step, 0.0, 1.0)
        self.bounds = bounds if bounds is not None else [0.0, 1.0]
        self.noise = max(0.0, _coerce_number(noise, 0.0))

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        context = _node_context(node, graph, status, params)
        current = _coerce_number(context.get("value"), 0.0)
        target = context["neighbor_mean"]
        if self.noise > 0.0:
            current += np.random.normal(0.0, self.noise)
        current = current + self.step * (target - current)
        low = 0.0
        high = 1.0
        if isinstance(self.bounds, (list, tuple)) and len(self.bounds) >= 2:
            low = _coerce_number(self.bounds[0], 0.0)
            high = _coerce_number(self.bounds[1], 1.0)
        current = _clamp(current, low, high)
        _set_opinion_value(graph, status, node, current)
        return self.compose(node, graph, status, status_map, params, kwargs)


class AttributeCoupling(NDQLBlockBase):
    def __init__(self, attribute=None, source=None, target=None, strength=0.5, bounds=None, **kwargs):
        super(AttributeCoupling, self).__init__(kwargs)
        self.attribute = attribute
        self.source = source if source is not None else attribute
        self.target = target if target is not None else attribute
        self.strength = _clamp(strength, 0.0, 1.0)
        self.bounds = bounds if bounds is not None else [0.0, 1.0]

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        context = _node_context(node, graph, status, params)
        source_value = context.get(self.source)
        if source_value is None and self.source in graph.nodes[node]:
            source_value = graph.nodes[node].get(self.source)
        if source_value is None:
            source_value = _get_opinion_value(graph, status, node)
        current = graph.nodes[node].get(self.target, source_value)
        current = _coerce_number(current, 0.0)
        source_value = _coerce_number(source_value, current)
        updated = current + self.strength * (source_value - current)
        if isinstance(self.bounds, (list, tuple)) and len(self.bounds) >= 2:
            updated = _clamp(updated, self.bounds[0], self.bounds[1])
        graph.nodes[node][self.target] = updated
        if self.target in {"status", "state"}:
            status[node] = updated
        return self.compose(node, graph, status, status_map, params, kwargs)


class OpinionAffectsInfection(NDQLBlockBase):
    def __init__(self, threshold=0.5, strength=0.5, target="infection_risk", invert=False, **kwargs):
        super(OpinionAffectsInfection, self).__init__(kwargs)
        self.threshold = _clamp(threshold, 0.0, 1.0)
        self.strength = _clamp(strength, 0.0, 1.0)
        self.target = target
        self.invert = bool(invert)

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        opinion = _get_opinion_value(graph, status, node)
        if self.invert:
            opinion = 1.0 - opinion
        risk = self.strength * opinion + (1.0 - self.strength) * self.threshold
        graph.nodes[node][self.target] = _clamp(risk, 0.0, 1.0)
        return self.compose(node, graph, status, status_map, params, kwargs)


class OpinionAffectsRecovery(NDQLBlockBase):
    def __init__(self, threshold=0.5, strength=0.5, target="recovery_rate", invert=False, **kwargs):
        super(OpinionAffectsRecovery, self).__init__(kwargs)
        self.threshold = _clamp(threshold, 0.0, 1.0)
        self.strength = _clamp(strength, 0.0, 1.0)
        self.target = target
        self.invert = bool(invert)

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        opinion = _get_opinion_value(graph, status, node)
        if self.invert:
            opinion = 1.0 - opinion
        recovery = self.threshold + self.strength * (opinion - self.threshold)
        graph.nodes[node][self.target] = _clamp(recovery, 0.0, 1.0)
        return self.compose(node, graph, status, status_map, params, kwargs)


class OpinionAffectsContactRate(NDQLBlockBase):
    def __init__(self, threshold=0.5, strength=0.5, target="contact_rate", invert=False, **kwargs):
        super(OpinionAffectsContactRate, self).__init__(kwargs)
        self.threshold = _clamp(threshold, 0.0, 1.0)
        self.strength = _clamp(strength, 0.0, 1.0)
        self.target = target
        self.invert = bool(invert)

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        opinion = _get_opinion_value(graph, status, node)
        if self.invert:
            opinion = 1.0 - opinion
        contact_rate = self.threshold + self.strength * (opinion - self.threshold)
        graph.nodes[node][self.target] = _clamp(contact_rate, 0.0, 1.0)
        return self.compose(node, graph, status, status_map, params, kwargs)


class InfectionAffectsOpinion(NDQLBlockBase):
    def __init__(self, source_statuses=None, target=0.5, strength=0.5, lag=0, direction="towards", **kwargs):
        super(InfectionAffectsOpinion, self).__init__(kwargs)
        self.source_statuses = _coerce_list(source_statuses) if source_statuses is not None else [1, "Infected", "I"]
        self.target = _clamp(target, 0.0, 1.0)
        self.strength = _clamp(strength, 0.0, 1.0)
        self.lag = max(0, int(lag or 0))
        self.direction = str(direction or "towards").lower()

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        current_status = status.get(node)
        labels = None
        if isinstance(params, dict):
            labels = params.get("model", {}).get("status_names") or params.get("model", {}).get("available_statuses")
        if not _status_matches(current_status, self.source_statuses, labels=labels):
            return self.compose(node, graph, status, status_map, params, kwargs)
        current = _get_opinion_value(graph, status, node)
        target = self.target
        if self.direction in {"away", "decrease", "down"}:
            target = 0.0 if target >= current else 1.0
        updated = current + self.strength * (target - current)
        _set_opinion_value(graph, status, node, _clamp(updated, 0.0, 1.0))
        return self.compose(node, graph, status, status_map, params, kwargs)


class StatusDependentOpinionUpdate(NDQLBlockBase):
    def __init__(self, status_filter=None, kernel=None, target="opinion", strength=0.5, fallback=0.5, **kwargs):
        super(StatusDependentOpinionUpdate, self).__init__(kwargs)
        self.status_filter = _coerce_list(status_filter) if status_filter is not None else None
        self.kernel = kernel
        self.target = target
        self.strength = _clamp(strength, 0.0, 1.0)
        self.fallback = _clamp(fallback, 0.0, 1.0)

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        labels = None
        if isinstance(params, dict):
            labels = params.get("model", {}).get("status_names") or params.get("model", {}).get("available_statuses")
        if not _status_matches(status.get(node), self.status_filter, labels=labels):
            return self.compose(node, graph, status, status_map, params, kwargs)
        context = _node_context(node, graph, status, params)
        current = _get_opinion_value(graph, status, node, self.fallback)
        if self.kernel is not None:
            next_value = _safe_eval(self.kernel, context, default=current)
        else:
            next_value = context["neighbor_mean"]
        updated = current + self.strength * (_coerce_number(next_value, current) - current)
        _set_opinion_value(graph, status, node, _clamp(updated, 0.0, 1.0))
        return self.compose(node, graph, status, status_map, params, kwargs)


class EpidemicDependentBias(NDQLBlockBase):
    def __init__(self, status_filter=None, status_weight=0.5, cross_status_factor=0.5, target="selection_bias", **kwargs):
        super(EpidemicDependentBias, self).__init__(kwargs)
        self.status_filter = _coerce_list(status_filter) if status_filter is not None else [1, "Infected", "I"]
        self.status_weight = _clamp(status_weight, 0.0, 1.0)
        self.cross_status_factor = _clamp(cross_status_factor, 0.0, 1.0)
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        current_status = status.get(node)
        labels = None
        if isinstance(params, dict):
            labels = params.get("model", {}).get("status_names") or params.get("model", {}).get("available_statuses")
        infected = 1.0 if _status_matches(current_status, self.status_filter, labels=labels) else 0.0
        bias = self.status_weight * infected + self.cross_status_factor * (1.0 - infected)
        graph.nodes[node][self.target] = _clamp(bias, 0.0, 1.0)
        return self.compose(node, graph, status, status_map, params, kwargs)


class PolicyIntervention(NDQLBlockBase):
    def __init__(self, start=0, end=None, target=None, action="scale", value=0.5, **kwargs):
        super(PolicyIntervention, self).__init__(kwargs)
        self.start = int(start or 0)
        self.end = None if end is None or end == "" else int(end)
        self.target = target
        self.action = str(action or "scale").lower()
        self.value = value

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        iteration = 0
        if isinstance(params, dict):
            iteration = int(params.get("model", {}).get("iteration", params.get("iteration", 0)) or 0)
        active = iteration >= self.start
        if active and self.end is not None:
            active = iteration <= self.end
        graph.graph["policy_active"] = active
        if not active or self.target is None:
            return self.compose(node, graph, status, status_map, params, kwargs)
        value = _coerce_number(self.value, 0.0)
        if self.action == "set":
            graph.nodes[node][self.target] = value
        elif self.action == "add":
            graph.nodes[node][self.target] = _coerce_number(graph.nodes[node].get(self.target, 0.0), 0.0) + value
        else:
            graph.nodes[node][self.target] = _coerce_number(graph.nodes[node].get(self.target, 0.0), 0.0) * value
        return self.compose(node, graph, status, status_map, params, kwargs)


class CommunityCoupling(NDQLBlockBase):
    def __init__(self, community_field="com", intra=1.0, inter=0.5, target="opinion", **kwargs):
        super(CommunityCoupling, self).__init__(kwargs)
        self.community_field = community_field
        self.intra = _clamp(intra, 0.0, 1.0)
        self.inter = _clamp(inter, 0.0, 1.0)
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        community = graph.nodes[node].get(self.community_field, graph.graph.get(self.community_field))
        same_values = []
        other_values = []
        for neigh in graph.neighbors(node):
            neigh_value = _get_opinion_value(graph, status, neigh)
            if graph.nodes[neigh].get(self.community_field, graph.graph.get(self.community_field)) == community:
                same_values.append(neigh_value)
            else:
                other_values.append(neigh_value)
        current = _get_opinion_value(graph, status, node)
        same_mean = float(np.mean(same_values)) if same_values else current
        other_mean = float(np.mean(other_values)) if other_values else current
        updated = current
        if same_values:
            updated = updated + self.intra * (same_mean - updated)
        if other_values:
            updated = updated + self.inter * (other_mean - updated)
        _set_opinion_value(graph, status, node, _clamp(updated, 0.0, 1.0))
        return self.compose(node, graph, status, status_map, params, kwargs)


class ExposureRate(NDQLBlockBase):
    def __init__(self, beta=0.1, contact_weight=1.0, mixing=1.0, infected_statuses=None, target="exposure", **kwargs):
        super(ExposureRate, self).__init__(kwargs)
        self.beta = _clamp(beta, 0.0, 1.0)
        self.contact_weight = _clamp(contact_weight, 0.0, 1.0)
        self.mixing = _clamp(mixing, 0.0, 1.0)
        self.infected_statuses = _coerce_list(infected_statuses) if infected_statuses is not None else [1, "Infected", "I"]
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        labels = None
        if isinstance(params, dict):
            labels = params.get("model", {}).get("available_statuses")
        neighbors = _iter_neighbors(graph, node)
        if not neighbors:
            exposure = 0.0
        else:
            infected = sum(1 for neigh in neighbors if _status_matches(status.get(neigh), self.infected_statuses, labels=labels))
            exposure = self.beta * self.contact_weight * self.mixing * (infected / float(len(neighbors)))
        graph.nodes[node][self.target] = _clamp(exposure, 0.0, 1.0)
        return self.compose(node, graph, status, status_map, params, kwargs)


class TransmissionKernel(NDQLBlockBase):
    def __init__(self, function=None, saturation=1.0, dose_response=None, source="exposure", target="transmission_probability", **kwargs):
        super(TransmissionKernel, self).__init__(kwargs)
        self.function = function
        self.saturation = _clamp(saturation, 0.0, 10.0)
        self.dose_response = dose_response
        self.source = source
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        context = _node_context(node, graph, status, params)
        exposure = _coerce_number(context.get(self.source, graph.nodes[node].get(self.source, 0.0)), 0.0)
        if self.function is not None:
            probability = _safe_eval(self.function, context, default=exposure)
        elif self.dose_response is not None:
            probability = _safe_eval(self.dose_response, context, default=exposure)
        else:
            probability = 1.0 - math.exp(-self.saturation * max(0.0, exposure))
        graph.nodes[node][self.target] = _clamp(probability, 0.0, 1.0)
        return self.compose(node, graph, status, status_map, params, kwargs)


class DoseResponseBlock(NDQLBlockBase):
    def __init__(self, shape="logistic", scale=1.0, offset=0.0, source="exposure", target="infection_probability", **kwargs):
        super(DoseResponseBlock, self).__init__(kwargs)
        self.shape = str(shape or "logistic").lower()
        self.scale = _coerce_number(scale, 1.0)
        self.offset = _coerce_number(offset, 0.0)
        self.source = source
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        context = _node_context(node, graph, status, params)
        exposure = _coerce_number(context.get(self.source, graph.nodes[node].get(self.source, 0.0)), 0.0)
        x = self.scale * (exposure - self.offset)
        if self.shape in {"linear", "line"}:
            value = x
        elif self.shape in {"step", "threshold"}:
            value = 1.0 if x >= 0 else 0.0
        else:
            value = 1.0 / (1.0 + math.exp(-x))
        graph.nodes[node][self.target] = _clamp(value, 0.0, 1.0)
        return self.compose(node, graph, status, status_map, params, kwargs)


class LatencyPeriod(NDQLBlockBase):
    def __init__(self, duration=1, distribution="fixed", target="latent", **kwargs):
        super(LatencyPeriod, self).__init__(kwargs)
        self.duration = max(1, int(duration or 1))
        self.distribution = str(distribution or "fixed").lower()
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        graph.nodes[node][self.target] = True
        graph.nodes[node]["latent_duration"] = self.duration
        graph.nodes[node]["latent_distribution"] = self.distribution
        return self.compose(node, graph, status, status_map, params, kwargs)


class IncubationState(NDQLBlockBase):
    def __init__(self, infectiousness=0.5, duration=1, target="incubating", **kwargs):
        super(IncubationState, self).__init__(kwargs)
        self.infectiousness = _clamp(infectiousness, 0.0, 1.0)
        self.duration = max(1, int(duration or 1))
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        graph.nodes[node][self.target] = True
        graph.nodes[node]["incubation_duration"] = self.duration
        graph.nodes[node]["infectiousness"] = self.infectiousness
        return self.compose(node, graph, status, status_map, params, kwargs)


class RecoveryKernel(NDQLBlockBase):
    def __init__(self, gamma=0.1, hazard=None, distribution=None, source="recovery_rate", **kwargs):
        super(RecoveryKernel, self).__init__(kwargs)
        self.gamma = _clamp(gamma, 0.0, 1.0)
        self.hazard = hazard
        self.distribution = distribution
        self.source = source

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        context = _node_context(node, graph, status, params)
        value = self.gamma
        if self.hazard is not None:
            value = _safe_eval(self.hazard, context, default=value)
        elif self.distribution is not None:
            value = _safe_eval(self.distribution, context, default=value)
        graph.nodes[node][self.source] = _clamp(value, 0.0, 1.0)
        return self.compose(node, graph, status, status_map, params, kwargs)


class WaningImmunity(NDQLBlockBase):
    def __init__(self, rate=0.1, delay=0, target="susceptibility", **kwargs):
        super(WaningImmunity, self).__init__(kwargs)
        self.rate = _clamp(rate, 0.0, 1.0)
        self.delay = max(0, int(delay or 0))
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        graph.nodes[node][self.target] = _clamp(self.rate, 0.0, 1.0)
        graph.nodes[node]["waning_delay"] = self.delay
        return self.compose(node, graph, status, status_map, params, kwargs)


class VaccinationBlock(NDQLBlockBase):
    def __init__(self, coverage=0.0, efficacy=1.0, priority=None, target="vaccinated", **kwargs):
        super(VaccinationBlock, self).__init__(kwargs)
        self.coverage = _clamp(coverage, 0.0, 1.0)
        self.efficacy = _clamp(efficacy, 0.0, 1.0)
        self.priority = priority
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        selected = _sample_bool(self.coverage)
        if self.priority is not None:
            selected = selected or bool(_safe_eval(str(self.priority), _node_context(node, graph, status, params), default=False))
        graph.nodes[node][self.target] = selected
        graph.nodes[node]["vaccine_efficacy"] = self.efficacy if selected else 0.0
        return self.compose(node, graph, status, status_map, params, kwargs)


class QuarantineBlock(NDQLBlockBase):
    def __init__(self, duration=1, trigger=None, coverage=1.0, target="quarantined", **kwargs):
        super(QuarantineBlock, self).__init__(kwargs)
        self.duration = max(1, int(duration or 1))
        self.trigger = trigger
        self.coverage = _clamp(coverage, 0.0, 1.0)
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        context = _node_context(node, graph, status, params)
        trigger = True if self.trigger is None else bool(_safe_eval(self.trigger, context, default=False))
        selected = trigger and _sample_bool(self.coverage)
        graph.nodes[node][self.target] = selected
        graph.nodes[node]["quarantine_duration"] = self.duration if selected else 0
        if selected:
            graph.nodes[node]["contact_rate"] = 0.0
        return self.compose(node, graph, status, status_map, params, kwargs)


class TestingBlock(NDQLBlockBase):
    def __init__(self, sensitivity=1.0, specificity=1.0, frequency=1, target="tested_positive", **kwargs):
        super(TestingBlock, self).__init__(kwargs)
        self.sensitivity = _clamp(sensitivity, 0.0, 1.0)
        self.specificity = _clamp(specificity, 0.0, 1.0)
        self.frequency = max(1, int(frequency or 1))
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        labels = None
        if isinstance(params, dict):
            labels = params.get("model", {}).get("available_statuses")
        infected = _status_matches(status.get(node), [1, "Infected", "I"], labels=labels)
        positive = _sample_bool(self.sensitivity if infected else (1.0 - self.specificity))
        graph.nodes[node][self.target] = positive
        graph.nodes[node]["testing_frequency"] = self.frequency
        return self.compose(node, graph, status, status_map, params, kwargs)


class TreatmentBlock(NDQLBlockBase):
    def __init__(self, efficacy=0.5, delay=0, capacity=None, target="treatment_effect", **kwargs):
        super(TreatmentBlock, self).__init__(kwargs)
        self.efficacy = _clamp(efficacy, 0.0, 1.0)
        self.delay = max(0, int(delay or 0))
        self.capacity = capacity
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        graph.nodes[node][self.target] = self.efficacy
        graph.nodes[node]["treatment_delay"] = self.delay
        graph.nodes[node]["treatment_capacity"] = self.capacity
        return self.compose(node, graph, status, status_map, params, kwargs)


class HospitalizationBlock(NDQLBlockBase):
    def __init__(self, capacity=None, rate=0.1, mortality=0.0, target="hospitalized", **kwargs):
        super(HospitalizationBlock, self).__init__(kwargs)
        self.capacity = capacity
        self.rate = _clamp(rate, 0.0, 1.0)
        self.mortality = _clamp(mortality, 0.0, 1.0)
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        graph.nodes[node][self.target] = _sample_bool(self.rate)
        graph.nodes[node]["hospital_mortality"] = self.mortality
        graph.nodes[node]["hospital_capacity"] = self.capacity
        return self.compose(node, graph, status, status_map, params, kwargs)


class MortalityBlock(NDQLBlockBase):
    def __init__(self, fatality=0.0, delay=0, cause=None, target_status="Removed", target="dead", **kwargs):
        super(MortalityBlock, self).__init__(kwargs)
        self.fatality = _clamp(fatality, 0.0, 1.0)
        self.delay = max(0, int(delay or 0))
        self.cause = cause
        self.target_status = target_status
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        dead = _sample_bool(self.fatality)
        graph.nodes[node][self.target] = dead
        graph.nodes[node]["mortality_delay"] = self.delay
        graph.nodes[node]["mortality_cause"] = self.cause
        if dead and self.target_status is not None:
            status[node] = self.target_status
        return self.compose(node, graph, status, status_map, params, kwargs)


class ReinfectionBlock(NDQLBlockBase):
    def __init__(self, susceptibility=1.0, cooldown=0, target="susceptibility", **kwargs):
        super(ReinfectionBlock, self).__init__(kwargs)
        self.susceptibility = _clamp(susceptibility, 0.0, 1.0)
        self.cooldown = max(0, int(cooldown or 0))
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        graph.nodes[node][self.target] = self.susceptibility
        graph.nodes[node]["reinfection_cooldown"] = self.cooldown
        return self.compose(node, graph, status, status_map, params, kwargs)


class StrainBlock(NDQLBlockBase):
    def __init__(self, strain_id=0, cross_immunity=0.0, fitness=1.0, target="strain_id", **kwargs):
        super(StrainBlock, self).__init__(kwargs)
        self.strain_id = strain_id
        self.cross_immunity = _clamp(cross_immunity, 0.0, 1.0)
        self.fitness = _clamp(fitness, 0.0, 10.0)
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        graph.nodes[node][self.target] = self.strain_id
        graph.nodes[node]["cross_immunity"] = self.cross_immunity
        graph.nodes[node]["strain_fitness"] = self.fitness
        return self.compose(node, graph, status, status_map, params, kwargs)


class SuperSpreaderBlock(NDQLBlockBase):
    def __init__(self, activity=1.0, burst_rate=0.0, target="activity", **kwargs):
        super(SuperSpreaderBlock, self).__init__(kwargs)
        self.activity = _coerce_number(activity, 1.0)
        self.burst_rate = _clamp(burst_rate, 0.0, 1.0)
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        graph.nodes[node][self.target] = self.activity
        graph.nodes[node]["burst_rate"] = self.burst_rate
        return self.compose(node, graph, status, status_map, params, kwargs)


class SeasonalityBlock(NDQLBlockBase):
    def __init__(self, period=1, amplitude=0.0, phase=0, target="seasonality_factor", **kwargs):
        super(SeasonalityBlock, self).__init__(kwargs)
        self.period = max(1, int(period or 1))
        self.amplitude = _clamp(amplitude, 0.0, 1.0)
        self.phase = int(phase or 0)
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        iteration = _graph_iteration(params)
        angle = 2.0 * math.pi * ((iteration + self.phase) % self.period) / float(self.period)
        factor = 1.0 + self.amplitude * math.sin(angle)
        graph.nodes[node][self.target] = factor
        return self.compose(node, graph, status, status_map, params, kwargs)


class ImportationBlock(NDQLBlockBase):
    def __init__(self, arrival_rate=0.0, source=None, target="imported", infectious_status="Infected", **kwargs):
        super(ImportationBlock, self).__init__(kwargs)
        self.arrival_rate = _clamp(arrival_rate, 0.0, 1.0)
        self.source = source
        self.target = target
        self.infectious_status = infectious_status

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        imported = _sample_bool(self.arrival_rate)
        graph.nodes[node][self.target] = imported
        if imported and self.infectious_status is not None:
            graph.nodes[node]["import_source"] = self.source
            status[node] = self.infectious_status
        return self.compose(node, graph, status, status_map, params, kwargs)


class RewiringBlock(NDQLBlockBase):
    def __init__(self, rewire_rate=0.0, preference=None, target="rewired", **kwargs):
        super(RewiringBlock, self).__init__(kwargs)
        self.rewire_rate = _clamp(rewire_rate, 0.0, 1.0)
        self.preference = preference
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        rewired = False
        if _sample_bool(self.rewire_rate):
            neighbors = _iter_neighbors(graph, node)
            if neighbors:
                old_neighbor = neighbors[np.random.randint(0, len(neighbors))]
                candidates = [n for n in graph.nodes() if n != node and not graph.has_edge(node, n)]
                if self.preference is not None:
                    try:
                        pref = str(self.preference)
                        candidates.sort(key=lambda n: abs(_coerce_number(graph.nodes[n].get(pref, 0.0), 0.0) - _coerce_number(graph.nodes[node].get(pref, 0.0), 0.0)))
                    except Exception:
                        pass
                if candidates:
                    new_neighbor = candidates[np.random.randint(0, len(candidates))]
                    if graph.has_edge(node, old_neighbor):
                        graph.remove_edge(node, old_neighbor)
                    graph.add_edge(node, new_neighbor)
                    rewired = True
        graph.nodes[node][self.target] = rewired
        return self.compose(node, graph, status, status_map, params, kwargs)


class CommunityMixingBlock(NDQLBlockBase):
    def __init__(self, intra_rate=1.0, inter_rate=0.5, community_field="com", target="mixing_rate", **kwargs):
        super(CommunityMixingBlock, self).__init__(kwargs)
        self.intra_rate = _clamp(intra_rate, 0.0, 1.0)
        self.inter_rate = _clamp(inter_rate, 0.0, 1.0)
        self.community_field = community_field
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        community = graph.nodes[node].get(self.community_field, graph.graph.get(self.community_field))
        same = 0
        diff = 0
        for neigh in _iter_neighbors(graph, node):
            if graph.nodes[neigh].get(self.community_field, graph.graph.get(self.community_field)) == community:
                same += 1
            else:
                diff += 1
        total = same + diff
        mixing = self.intra_rate if total == 0 else ((same / float(total)) * self.intra_rate + (diff / float(total)) * self.inter_rate)
        graph.nodes[node][self.target] = _clamp(mixing, 0.0, 1.0)
        return self.compose(node, graph, status, status_map, params, kwargs)


class EdgeActivationBlock(NDQLBlockBase):
    def __init__(self, threshold=0.5, duration=1, target="active", **kwargs):
        super(EdgeActivationBlock, self).__init__(kwargs)
        self.threshold = _clamp(threshold, 0.0, 1.0)
        self.duration = max(1, int(duration or 1))
        self.target = target

    def execute(self, node, graph, status, status_map, params=None, *args, **kwargs):
        active = _sample_bool(self.threshold)
        graph.nodes[node][self.target] = active
        graph.nodes[node]["activation_duration"] = self.duration
        for neigh in _iter_neighbors(graph, node):
            if graph.has_edge(node, neigh):
                graph.edges[node, neigh]["active"] = active
        return self.compose(node, graph, status, status_map, params, kwargs)


__all__ = [
    "NDQLBlockBase",
    "Parameter",
    "Constant",
    "Variable",
    "Distribution",
    "Compose",
    "Filter",
    "Selector",
    "Aggregator",
    "Kernel",
    "Transform",
    "ClampNormalize",
    "Schedule",
    "Observe",
    "OpinionDistribution",
    "OpinionStubbornness",
    "OpinionNoise",
    "OpinionPolarization",
    "OpinionMediaInfluence",
    "OpinionTrustFilter",
    "OpinionConsensusBlock",
    "OpinionRepulsion",
    "OpinionAssimilation",
    "OpinionExternalField",
    "OpinionMultiTopic",
    "OpinionLabelSwitch",
    "OpinionBoundedDrift",
    "AttributeCoupling",
    "OpinionAffectsInfection",
    "OpinionAffectsRecovery",
    "OpinionAffectsContactRate",
    "InfectionAffectsOpinion",
    "StatusDependentOpinionUpdate",
    "EpidemicDependentBias",
    "PolicyIntervention",
    "CommunityCoupling",
    "ExposureRate",
    "TransmissionKernel",
    "DoseResponseBlock",
    "LatencyPeriod",
    "IncubationState",
    "RecoveryKernel",
    "WaningImmunity",
    "VaccinationBlock",
    "QuarantineBlock",
    "TestingBlock",
    "TreatmentBlock",
    "HospitalizationBlock",
    "MortalityBlock",
    "ReinfectionBlock",
    "StrainBlock",
    "SuperSpreaderBlock",
    "SeasonalityBlock",
    "ImportationBlock",
    "RewiringBlock",
    "CommunityMixingBlock",
    "EdgeActivationBlock",
]
