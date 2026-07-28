import math
import statistics

import networkx as nx
import numpy as np

from ndlib.models.compartments.Compartment import Compartiment, ConfigurationException
from ndlib.models.compartments.ConditionalComposition import ConditionalComposition

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
]
