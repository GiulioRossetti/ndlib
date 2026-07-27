import http.server
import importlib
import json
import os
import sys
import webbrowser
import socket
import inspect
from urllib.parse import urlparse, parse_qs
import numpy as np
import networkx as nx
from networkx.algorithms import community as nx_community

# Add the repository root to the front of the import path so the dashboard
# always uses the source tree currently being edited, not an installed copy.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import ndlib.models.epidemics as epd
import ndlib.models.opinions as opn
import ndlib.models.ModelConfig as mc

__author__ = "Antigravity"
__license__ = "BSD-2-Clause"

PORT = 5000
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "dist")
COMMUNITY_ASSIGNMENT_MODELS = {"ICEModel", "ICPModel", "ICEPModel"}
COMMUNITY_DETECTION_ALGORITHMS = [
    {"value": "louvain_communities", "label": "Louvain"},
    {"value": "greedy_modularity_communities", "label": "Greedy Modularity"},
    {"value": "naive_greedy_modularity_communities", "label": "Naive Greedy Modularity"},
    {"value": "label_propagation_communities", "label": "Label Propagation"},
    {"value": "asyn_lpa_communities", "label": "Async Label Propagation"},
    {"value": "fast_label_propagation_communities", "label": "Fast Label Propagation"},
    {"value": "girvan_newman", "label": "Girvan-Newman"},
    {"value": "asyn_fluidc", "label": "Async Fluid Communities"},
]
CONTINUOUS_OPINION_BLOCK_TYPES = {
    "OpinionDistanceThreshold",
    "OpinionSelectionBias",
    "OpinionCompromise",
}


def sanitize_for_json(obj):
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [sanitize_for_json(x) for x in obj]
    elif isinstance(obj, type):
        return obj.__name__
    elif isinstance(obj, (np.int64, np.int32, np.integer)):
        return int(obj)
    elif isinstance(obj, (float, np.float64, np.float32, np.floating)):
        val = float(obj)
        import math
        if math.isinf(val) or math.isnan(val):
            return None
        return val
    elif callable(obj):
        try:
            val = obj()
            return sanitize_for_json(val)
        except Exception:
            return str(obj)
    return obj


def is_threshold_parameter(param, p_info):
    name = str(param or "").lower()
    descr = str((p_info or {}).get("descr", "")).lower()
    return "threshold" in name or "threshold" in descr or name == "epsilon"


def clamp_unit_float(value, fallback=0.1):
    try:
        val = float(value)
    except (TypeError, ValueError):
        return float(fallback)
    return min(1.0, max(0.0, val))


def coerce_model_parameter_value(param, val, p_info):
    """
    Coerce dashboard payload values to the type expected by the model.

    The dashboard sends JSON values, so integer-only parameters such as q/k
    can arrive as floats or numeric strings. Continuous opinion parameters must
    stay as floats even when their defaults are integers.
    """
    if val is None:
        default_val = p_info.get("default")
        if callable(default_val):
            try:
                default_val = default_val()
            except Exception:
                default_val = None

        if isinstance(default_val, (int, float, np.integer, np.floating)) and not isinstance(default_val, bool):
            return default_val

        range_info = p_info.get("range")
        int_params = {"q", "k", "iterations"}
        if (isinstance(default_val, int) and not isinstance(default_val, bool)) or param in int_params:
            return 1
        if is_threshold_parameter(param, p_info) or range_info == [0, 1]:
            return clamp_unit_float(0.1, 0.1)
        if range_info == [-1, 1]:
            return 0.0
        return 0.1

    if isinstance(val, str) and not val.strip():
        return coerce_model_parameter_value(param, None, p_info)

    if isinstance(val, bool) or isinstance(val, (list, tuple, dict, set)):
        return val

    default_val = p_info.get("default")
    if callable(default_val):
        try:
            default_val = default_val()
        except Exception:
            default_val = None

    range_info = p_info.get("range")
    int_params = {"q", "k", "iterations"}

    # Coerce count-like parameters to positive integers.
    if param in int_params:
        try:
            return max(1, int(round(float(val))))
        except (ValueError, TypeError):
            try:
                return max(1, int(val))
            except (ValueError, TypeError):
                return val

    if isinstance(default_val, int) and not isinstance(default_val, bool):
        try:
            return int(round(float(val)))
        except (ValueError, TypeError):
            try:
                return int(val)
            except (ValueError, TypeError):
                return val

    if is_threshold_parameter(param, p_info) or range_info == [0, 1]:
        return clamp_unit_float(val, p_info.get("default", 0.1))

    if isinstance(default_val, float) or range_info == [0, 1] or range_info == [-1, 1]:
        return float(val)

    if range_info is float:
        return float(val)

    if isinstance(val, str):
        try:
            if any(ch in val for ch in [".", "e", "E"]):
                return float(val)
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return val

    if isinstance(val, (int, np.integer)):
        return int(val)
    if isinstance(val, (float, np.floating)):
        if np.isnan(val):
            return coerce_model_parameter_value(param, None, p_info)
        return float(val)

    return val


def normalize_iteration_counts(raw_value, statuses):
    """
    Normalize iteration outputs so the dashboard always receives a status->count map.
    """
    if isinstance(raw_value, dict):
        return {str(k): int(v) for k, v in raw_value.items()}

    status_codes = list(statuses.values()) if isinstance(statuses, dict) else []
    if len(status_codes) == 1:
        return {str(status_codes[0]): int(raw_value)}

    return {"total": int(raw_value)}


def normalize_iteration_record(it):
    """
    Normalize a raw iteration item into a dict.

    Some model implementations return plain dicts, while a few historical
    code paths may yield tuples/lists containing one or more dict fragments.
    The dashboard only needs the merged dict form.
    """
    if isinstance(it, dict):
        return it

    if isinstance(it, (list, tuple)) and len(it) >= 2 and isinstance(it[0], (int, np.integer)):
        payload = it[1]
        if isinstance(payload, (list, tuple)) and len(payload) == 3:
            delta, node_count, status_delta = payload
            normalized = {
                "iteration": int(it[0]),
                "status": delta if isinstance(delta, dict) else {},
                "node_count": node_count if isinstance(node_count, dict) else {},
                "status_delta": status_delta if isinstance(status_delta, dict) else {},
            }
            if len(it) > 2:
                for extra in it[2:]:
                    if isinstance(extra, dict):
                        normalized.update(extra)
            return normalized

        if isinstance(payload, dict):
            normalized = {
                "iteration": int(it[0]),
                "status": payload,
                "node_count": {},
                "status_delta": {},
            }
            if len(it) > 2:
                for extra in it[2:]:
                    if isinstance(extra, dict):
                        normalized.update(extra)
            return normalized

    if isinstance(it, (list, tuple)):
        merged = {}
        for part in it:
            if isinstance(part, dict):
                merged.update(part)
        if merged:
            return merged

    return {
        "iteration": 0,
        "status": {},
        "node_count": {},
        "status_delta": {},
    }


def _extract_continuous_scalar(value):
    if isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool):
        return float(value)

    if isinstance(value, dict):
        for nested in value.values():
            scalar = _extract_continuous_scalar(nested)
            if scalar is not None:
                return scalar

    if isinstance(value, (list, tuple)):
        for nested in value:
            scalar = _extract_continuous_scalar(nested)
            if scalar is not None:
                return scalar

    return None


def build_absolute_status_history(iterations, nodes):
    """
    Reconstruct a cumulative per-node history from sparse iteration payloads.
    """
    node_ids = [str(node.get("id")) if isinstance(node, dict) else str(node) for node in nodes]
    history = []
    current_status = {node_id: 0.0 for node_id in node_ids}

    for it in iterations or []:
        status_map = it.get("status", {}) if isinstance(it, dict) else {}
        if not isinstance(status_map, dict):
            status_map = {}

        for node_id in node_ids:
            raw_value = None
            if node_id in status_map:
                raw_value = status_map[node_id]
            else:
                try:
                    numeric_id = int(node_id)
                    if numeric_id in status_map:
                        raw_value = status_map[numeric_id]
                except (TypeError, ValueError):
                    pass

            if raw_value is None:
                continue

            scalar = _extract_continuous_scalar(raw_value)
            if scalar is not None:
                current_status[node_id] = scalar

        history.append(current_status.copy())

    return history


def build_initial_status_assignment(graph, available_statuses, percentages):
    """
    Build a concrete node -> status-name assignment from percentage inputs.

    Percentages are normalized if they do not sum to 100. Nodes are assigned
    by shuffling the node list and slicing it according to the requested share
    for each status.
    """
    nodes = list(graph.nodes())
    status_names = list(available_statuses.keys()) if isinstance(available_statuses, dict) else list(available_statuses)
    if not nodes or not status_names:
        return {}

    requested = {}
    total = 0.0
    for status_name in status_names:
        raw_value = 0.0
        if isinstance(percentages, dict) and status_name in percentages:
            raw_value = percentages[status_name]
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            value = 0.0
        if value < 0:
            value = 0.0
        requested[status_name] = value
        total += value

    if total <= 0:
        requested = {status_name: 1.0 for status_name in status_names}
        total = float(len(status_names))

    fractions = [requested[status_name] / total for status_name in status_names]
    counts = [int(np.floor(frac * len(nodes))) for frac in fractions]
    remainder = len(nodes) - sum(counts)
    for idx in range(remainder):
        counts[idx % len(counts)] += 1

    shuffled_nodes = list(np.random.permutation(nodes))
    assignment = {}
    cursor = 0
    for status_name, count in zip(status_names[:-1], counts[:-1]):
        for node in shuffled_nodes[cursor: cursor + count]:
            assignment[node] = status_name
        cursor += count

    last_status = status_names[-1]
    for node in shuffled_nodes[cursor:]:
        assignment[node] = last_status

    return assignment


def build_node_binary_configuration(graph, param_name, selected_nodes):
    """
    Build a binary node configuration where selected nodes receive 1 and the
    remaining nodes receive 0.
    """
    selected_set = set(selected_nodes or [])
    node_cfg = {}
    for node in graph.nodes():
        node_cfg[node] = 1 if node in selected_set else 0
    return {param_name: node_cfg}


def build_community_assignment(graph):
    """
    Build a deterministic node -> community label mapping.

    Community-based models in NDLib expect a node configuration named ``com``.
    When the dashboard does not receive that data from the user, we derive it
    from the graph structure using NetworkX community detection.
    """
    return build_community_assignment_with_algorithm(graph, "louvain_communities")


def build_community_assignment_with_algorithm(graph, algorithm="louvain_communities", k=None):
    nodes = list(graph.nodes())
    if len(nodes) == 0:
        return {}

    if len(nodes) == 1 or graph.number_of_edges() == 0:
        return {n: 0 for n in nodes}

    base_graph = graph.to_undirected() if graph.is_directed() else graph

    communities = []
    seed = 42

    def _community_list(result):
        if result is None:
            return []
        if isinstance(result, (list, tuple, set)):
            return [set(c) for c in result]
        return [set(c) for c in list(result)]

    try:
        if algorithm == "greedy_modularity_communities":
            communities = _community_list(nx_community.greedy_modularity_communities(base_graph))
        elif algorithm == "naive_greedy_modularity_communities":
            communities = _community_list(nx_community.naive_greedy_modularity_communities(base_graph))
        elif algorithm == "louvain_communities":
            communities = _community_list(nx_community.louvain_communities(base_graph, seed=seed))
        elif algorithm == "asyn_lpa_communities":
            communities = _community_list(nx_community.asyn_lpa_communities(base_graph, seed=seed))
        elif algorithm == "fast_label_propagation_communities":
            communities = _community_list(nx_community.fast_label_propagation_communities(base_graph))
        elif algorithm == "label_propagation_communities":
            communities = _community_list(nx_community.label_propagation_communities(base_graph))
        elif algorithm == "girvan_newman":
            communities = _community_list(next(nx_community.girvan_newman(base_graph)))
        elif algorithm == "asyn_fluidc":
            k_val = int(k) if k is not None else 2
            if k_val < 2 or k_val > len(nodes) or not nx.is_connected(base_graph):
                raise ValueError("asyn_fluidc requires a connected graph and 2 <= k <= number of nodes")
            communities = _community_list(nx_community.asyn_fluidc(base_graph, k_val, seed=seed))
        else:
            communities = _community_list(nx_community.louvain_communities(base_graph, seed=seed))
    except Exception:
        communities = []

    if not communities:
        communities = [set(component) for component in nx.connected_components(base_graph)]

    def _sort_key(group):
        sample = min((str(n) for n in group), default="")
        return sample

    community_map = {}
    for community_id, group in enumerate(sorted(communities, key=_sort_key)):
        for node in group:
            community_map[node] = community_id

    for node in nodes:
        community_map.setdefault(node, 0)

    return community_map


def needs_community_assignment(model_instance):
    return model_instance.__class__.__name__ in COMMUNITY_ASSIGNMENT_MODELS


def resolve_model_class(category, model_class_name):
    """
    Resolve a model class from the local source tree or dynamic custom models.
    """
    if category == "Custom Models":
        full_module_name = "ndlib.dashboard.custom_models.%s" % model_class_name
        try:
            if full_module_name in sys.modules:
                mod = sys.modules[full_module_name]
            else:
                mod = importlib.import_module(full_module_name)
            if hasattr(mod, model_class_name):
                return getattr(mod, model_class_name)
        except Exception as e:
            print("Error resolving custom model class %s: %s" % (model_class_name, str(e)))
            pass
        return None

    package = opn if category == "Opinions" else epd

    if hasattr(package, model_class_name):
        return getattr(package, model_class_name)

    module_prefix = "ndlib.models.opinions" if category == "Opinions" else "ndlib.models.epidemics"
    try:
        module = importlib.import_module(f"{module_prefix}.{model_class_name}")
        if hasattr(module, model_class_name):
            return getattr(module, model_class_name)
    except Exception:
        pass

    for _, obj in inspect.getmembers(package, inspect.isclass):
        if obj.__name__ == model_class_name:
            return obj

    raise AttributeError(f"module '{package.__name__}' has no attribute '{model_class_name}'")


def build_graph_from_payload(graph_type, graph_params):
    seed = 42
    if graph_type == "erdos_renyi":
        g = nx.erdos_renyi_graph(
            int(graph_params.get("n", 100)),
            float(graph_params.get("p", 0.1)),
            seed=seed
        )
    elif graph_type == "barabasi_albert":
        g = nx.barabasi_albert_graph(
            int(graph_params.get("n", 100)),
            int(graph_params.get("m", 2)),
            seed=seed
        )
    elif graph_type == "watts_strogatz":
        g = nx.watts_strogatz_graph(
            int(graph_params.get("n", 100)),
            int(graph_params.get("k", 4)),
            float(graph_params.get("p", 0.1)),
            seed=seed
        )
    elif graph_type == "complete":
        g = nx.complete_graph(int(graph_params.get("n", 100)))
    elif graph_type == "lfr":
        n = int(graph_params.get("n", 100))
        tau1 = float(graph_params.get("tau1", 2.0))
        tau2 = float(graph_params.get("tau2", 1.5))
        mu = float(graph_params.get("mu", 0.1))
        average_degree = int(graph_params.get("average_degree", 8))
        min_degree = int(graph_params.get("min_degree", 3))
        min_community = int(graph_params.get("min_community", 20))
        max_iters = int(graph_params.get("max_iters", 500))

        lfr_candidates = []
        requested_min_community = max(2, min(min_community, n - 1))
        for candidate_min_community in [
            requested_min_community,
            max(requested_min_community, max(4, n // 5)),
            max(requested_min_community, max(4, n // 4)),
            max(requested_min_community, max(4, n // 3)),
            max(requested_min_community, max(4, n // 2)),
        ]:
            candidate_min_community = min(candidate_min_community, n - 1)
            lfr_candidates.append({
                "mu": mu,
                "average_degree": max(2, min(average_degree, n - 1)),
                "min_community": candidate_min_community,
            })
            lfr_candidates.append({
                "mu": mu,
                "min_degree": max(1, min(min_degree, n - 1)),
                "min_community": candidate_min_community,
            })

        g = None
        for candidate in lfr_candidates:
            try:
                g = nx.LFR_benchmark_graph(
                    n,
                    tau1,
                    tau2,
                    candidate["mu"],
                    average_degree=candidate.get("average_degree"),
                    min_degree=candidate.get("min_degree"),
                    min_community=candidate["min_community"],
                    max_iters=max_iters,
                    seed=seed
                )
                break
            except Exception:
                continue

        if g is None:
            raise ValueError("Unable to generate an LFR benchmark graph with the selected parameters")
        g = nx.Graph(g)
        community_lookup = {}
        next_community_id = 0
        for node, attrs in g.nodes(data=True):
            community = attrs.get("community")
            if community is None:
                attrs["com"] = 0
                continue
            community_key = frozenset(community)
            if community_key not in community_lookup:
                community_lookup[community_key] = next_community_id
                next_community_id += 1
            attrs["com"] = community_lookup[community_key]
        for node in g.nodes():
            g.nodes[node]["com"] = g.nodes[node].get("com", 0)
    elif graph_type == "planted_partition":
        groups = int(graph_params.get("community_groups", 4))
        group_size = int(graph_params.get("community_size", 25))
        p_in = float(graph_params.get("p_in", 0.25))
        p_out = float(graph_params.get("p_out", 0.02))
        g = nx.planted_partition_graph(groups, group_size, p_in, p_out, seed=seed)
        for node in g.nodes():
            g.nodes[node]["com"] = int(node // group_size)
    elif graph_type == "stochastic_block_model":
        groups = int(graph_params.get("community_groups", 4))
        group_size = int(graph_params.get("community_size", 25))
        p_in = float(graph_params.get("p_in", 0.25))
        p_out = float(graph_params.get("p_out", 0.02))
        sizes = [group_size for _ in range(groups)]
        probs = [[p_in if i == j else p_out for j in range(groups)] for i in range(groups)]
        g = nx.stochastic_block_model(sizes, probs, seed=seed)
        start = 0
        for community_id, size in enumerate(sizes):
            for node in range(start, start + size):
                g.nodes[node]["com"] = community_id
            start += size
    elif graph_type == "upload":
        content = graph_params.get("file_content", "")
        fmt = graph_params.get("file_format", "graphml")
        if fmt == "graphml":
            g = nx.parse_graphml(content)
        elif fmt == "gml":
            g = nx.parse_gml(content)
        else:
            g = nx.parse_edgelist(content.splitlines())
    else:
        raise ValueError("Unknown graph type: %s" % graph_type)

    if graph_params.get("directed", False):
        g = g.to_directed()

    return g


def deserialize_node_id(node_id):
    if isinstance(node_id, str):
        stripped = node_id.strip()
        if stripped:
            try:
                return int(stripped)
            except ValueError:
                return node_id
    return node_id


def serialize_graph_for_frontend(g):
    pos = nx.spring_layout(g)
    nodes_data = []
    for n in g.nodes():
        attrs = g.nodes[n]
        nodes_data.append({
            "id": str(n),
            "label": str(n),
            "x": float(pos[n][0] * 500),
            "y": float(pos[n][1] * 500),
            "com": int(attrs["com"]) if "com" in attrs and attrs["com"] is not None else None,
        })

    edges_data = []
    for u, v in g.edges():
        edges_data.append({
            "source": str(u),
            "target": str(v)
        })

    return {
        "nodes": nodes_data,
        "edges": edges_data,
        "node_count": g.number_of_nodes(),
        "edge_count": g.number_of_edges(),
        "directed": g.is_directed(),
    }


def build_graph_from_serialized(graph_data):
    if not isinstance(graph_data, dict):
        raise ValueError("Invalid graph_data payload")

    directed = bool(graph_data.get("directed", False))
    g = nx.DiGraph() if directed else nx.Graph()

    nodes = graph_data.get("nodes", [])
    for node in nodes:
        if isinstance(node, dict):
            node_id = node.get("id")
            node_attrs = {}
            if node.get("com") is not None:
                try:
                    node_attrs["com"] = int(node.get("com"))
                except (TypeError, ValueError):
                    node_attrs["com"] = node.get("com")
        else:
            node_id = node
            node_attrs = {}
        node_id = deserialize_node_id(node_id)
        if node_id is not None:
            g.add_node(node_id, **node_attrs)

    for edge in graph_data.get("edges", []):
        if isinstance(edge, dict):
            source = edge.get("source")
            target = edge.get("target")
        elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
            source, target = edge[0], edge[1]
        else:
            continue
        source = deserialize_node_id(source)
        target = deserialize_node_id(target)
        if source is not None and target is not None:
            g.add_edge(source, target)

    if g.number_of_nodes() == 0 and graph_data.get("node_count"):
        for idx in range(int(graph_data["node_count"])):
            g.add_node(str(idx))

    return g


def generate_custom_model_class(model_data):
    """
    Generates a Python source string representing a CompositeModel subclass
    based on custom visual model JSON data.
    """
    model_name = model_data.get("name", "CustomModel")
    class_name = "".join(c for c in model_name if c.isalnum() or c == "_")
    if not class_name or not class_name[0].isalpha() and class_name[0] != "_":
        class_name = "_" + class_name

    statuses = model_data.get("statuses", [])
    compartments = model_data.get("compartments", [])
    rules = model_data.get("rules", [])
    initial_status = model_data.get("initial_status", [])
    opinion_variables = sorted({
        comp.get("params", {}).get("var", "")
        for comp in compartments
        if comp.get("type") == "NodeNumericalVariable"
        and comp.get("params", {}).get("var_type") == "ATTRIBUTE"
        and comp.get("params", {}).get("var") == "opinion"
    })
    uses_continuous_opinion_initialization = bool(
        opinion_variables
        or model_data.get("use_case") == "continuous_opinions"
        or model_data.get("template_id") == "algorithmic_bias"
    )
    initial_opinion_distribution = model_data.get("initial_opinion_distribution", "uniform")
    continuous_opinion_mode = bool(
        uses_continuous_opinion_initialization
        or any(comp.get("type") in CONTINUOUS_OPINION_BLOCK_TYPES for comp in compartments)
    )

    if continuous_opinion_mode:
        return generate_continuous_opinion_custom_model_class(
            model_data,
            class_name,
            statuses,
            compartments,
            rules,
            initial_status,
            initial_opinion_distribution,
        )

    code = [
        "import numpy as np",
        "from ndlib.models.CompositeModel import CompositeModel",
        "from ndlib.models.compartments.NodeStochastic import NodeStochastic",
        "from ndlib.models.compartments.NodeThreshold import NodeThreshold",
        "from ndlib.models.compartments.NodeCategoricalAttribute import NodeCategoricalAttribute",
        "from ndlib.models.compartments.NodeNumericalAttribute import NodeNumericalAttribute",
        "from ndlib.models.compartments.NodeNumericalVariable import NodeNumericalVariable",
        "from ndlib.models.compartments.EdgeStochastic import EdgeStochastic",
        "from ndlib.models.compartments.EdgeCategoricalAttribute import EdgeCategoricalAttribute",
        "from ndlib.models.compartments.EdgeNumericalAttribute import EdgeNumericalAttribute",
        "from ndlib.models.compartments.ConditionalComposition import ConditionalComposition",
        "from ndlib.models.compartments.CountDown import CountDown",
        "from ndlib.models.compartments.enums.NumericalType import NumericalType",
        "from ndlib.models.opinions.initial_opinion_distribution import sample_initial_opinions",
        "",
        "class %s(CompositeModel):" % class_name,
        "    def __init__(self, graph, seed=None):",
        "        # Bypass CompositeModel.__init__ to avoid recursion bug in super(self.__class__, self)",
        "        from ndlib.models.DiffusionModel import DiffusionModel",
        "        DiffusionModel.__init__(self, graph, seed=seed)",
        "        self.available_statuses = {}",
        "        self.compartment = {}",
        "        self.compartment_progressive = 0",
        "        self.status_progressive = 0",
        "        self.name = %r" % model_name,
        "        self.discrete_state = True",
        "        self.available_statuses = {"
    ]

    for idx, status in enumerate(statuses):
        code.append("            %r: %d," % (status["name"], idx))
    code.append("        }")
    
    code.append("        self.parameters = {")
    code.append("            'model': {")
    if uses_continuous_opinion_initialization:
        code.append("                'initial_opinion_distribution': {")
        code.append("                    'descr': 'Initial opinion distribution in [0, 1]',")
        code.append("                    'choices': [")
        code.append("                        {'value': 'uniform', 'label': 'Uniform'},")
        code.append("                        {'value': 'normal', 'label': 'Normal'},")
        code.append("                        {'value': 'gaussian', 'label': 'Gaussian'},")
        code.append("                        {'value': 'bimodal', 'label': 'Bimodal'},")
        code.append("                        {'value': 'left_skewed', 'label': 'Left skewed'},")
        code.append("                        {'value': 'right_skewed', 'label': 'Right skewed'},")
        code.append("                        {'value': 'polarized', 'label': 'Polarized'},")
        code.append("                    ],")
        code.append("                    'optional': True,")
        code.append("                    'default': %r" % initial_opinion_distribution)
        code.append("                },")
    for status in statuses:
        ratio = 0.0
        for init in initial_status:
            if init["status"] == status["name"]:
                ratio = float(init.get("ratio", 0.0))
        code.append("                'percentage_%s': {" % status["name"])
        code.append("                    'descr': 'Initial percentage of %s nodes'," % status["name"])
        code.append("                    'range': [0, 1],")
        code.append("                    'optional': True,")
        code.append("                    'default': %f" % ratio)
        code.append("                },")
    code.append("            },")
    code.append("            'nodes': {},")
    code.append("            'edges': {}")
    code.append("        }")

    code.append("")
    code.append("        # Add statuses")
    for status in statuses:
        code.append("        self.add_status(%r)" % status["name"])

    code.append("")
    code.append("        # Define compartments")
    # Sort compartments: simple dependency sorting for ConditionalComposition
    sorted_comps = []
    pending = list(compartments)
    defined_names = set()
    
    for _ in range(10):
        if not pending:
            break
        next_pending = []
        for comp in pending:
            comp_type = comp["type"]
            params = comp.get("params", {})
            
            deps = []
            if comp_type == "ConditionalComposition":
                if params.get("condition"): deps.append(params["condition"])
                if params.get("first_branch"): deps.append(params["first_branch"])
                if params.get("second_branch"): deps.append(params["second_branch"])
            
            if all(d in defined_names for d in deps):
                sorted_comps.append(comp)
                defined_names.add(comp["name"])
            else:
                next_pending.append(comp)
        pending = next_pending
    for comp in pending:
        sorted_comps.append(comp)

    for comp in sorted_comps:
        comp_name = comp["name"]
        comp_type = comp["type"]
        params = comp.get("params", {})
        
        args = []
        for k, v in params.items():
            if k == "triggering_status":
                args.append("triggering_status=%r" % v)
            elif comp_type == "ConditionalComposition" and k in {"condition", "first_branch", "second_branch"}:
                args.append("%s=%s" % (k, str(v)))
            elif comp_type == "NodeNumericalVariable" and k in {"var_type", "value_type"}:
                if v:
                    args.append("%s=NumericalType.%s" % (k, str(v).upper()))
            elif (comp_type in {"NodeNumericalAttribute", "EdgeNumericalAttribute"}) and k == "value" and params.get("op") == "IN" and isinstance(v, str) and "," in v:
                try:
                    lst = [float(x.strip()) for x in v.split(",")]
                    args.append("value=%r" % lst)
                except ValueError:
                    args.append("value=%r" % v)
            elif isinstance(v, str):
                try:
                    args.append("%s=%s" % (k, str(float(v))))
                except ValueError:
                    args.append("%s=%r" % (k, v))
            else:
                args.append("%s=%s" % (k, str(v)))
        
        code.append("        %s = %s(%s)" % (comp_name, comp_type, ", ".join(args)))

    code.append("")
    code.append("        # Define rules")
    for rule in rules:
        code.append("        self.add_rule(%r, %r, %s)" % (rule["from"], rule["to"], rule["using"]))

    code.append("")
    code.append("    def set_initial_status(self, configuration):")
    code.append("        configuration = configuration or None")
    code.append("        model_params = configuration.get_model_parameters() if configuration is not None else {}")
    code.append("        nodes_cfg = configuration.get_nodes_configuration() if configuration is not None else {}")
    code.append("        edges_cfg = configuration.get_edges_configuration() if configuration is not None else {}")
    code.append("        status_cfg = configuration.get_model_configuration() if configuration is not None else {}")
    code.append("")
    code.append("        self.params['nodes'] = {}")
    code.append("        self.params['edges'] = {}")
    code.append("        self.params['status'] = {}")
    code.append("        self.params['model'] = {}")
    code.append("")
    code.append("        for param, param_info in self.parameters['model'].items():")
    code.append("            self.params['model'][param] = model_params.get(param, param_info.get('default'))")
    code.append("")
    code.append("        for param, node_to_value in nodes_cfg.items():")
    code.append("            if len(node_to_value) < len(self.graph.nodes):")
    code.append("                raise ValueError({'message': 'Not all nodes have a configuration specified'})")
    code.append("            self.params['nodes'][param] = node_to_value")
    code.append("")
    code.append("        for param, edge_to_values in edges_cfg.items():")
    code.append("            if len(edge_to_values) == len(self.graph.edges):")
    code.append("                self.params['edges'][param] = {}")
    code.append("                for e in edge_to_values:")
    code.append("                    self.params['edges'][param][e] = edge_to_values[e]")
    code.append("")
    code.append("        for status_name, nodes in status_cfg.items():")
    code.append("            self.params['status'][status_name] = nodes")
    code.append("            if status_name in self.available_statuses:")
    code.append("                for node in nodes:")
    code.append("                    self.status[node] = self.available_statuses[status_name]")
    if uses_continuous_opinion_initialization:
        code.append("")
        code.append("        opinion_distribution = self.params['model'].get('initial_opinion_distribution', %r)" % initial_opinion_distribution)
        code.append("        sampled_opinions = sample_initial_opinions(len(self.graph.nodes), opinion_distribution)")
        code.append("        for node, opinion in zip(self.graph.nodes, sampled_opinions):")
        code.append("            self.graph.nodes[node]['opinion'] = float(opinion)")
    code.append("")
    code.append("        pcts = {}")
    code.append("        for status_name in self.available_statuses:")
    code.append("            param_key = 'percentage_%s' % status_name")
    code.append("            if param_key in self.params['model']:")
    code.append("                pcts[status_name] = float(self.params['model'][param_key])")
    code.append("        if pcts:")
    code.append("            nodes = list(self.graph.nodes)")
    code.append("            np.random.shuffle(nodes)")
    code.append("            current_idx = 0")
    code.append("            n_nodes = len(nodes)")
    code.append("            for status_name, pct in pcts.items():")
    code.append("                count = int(round(pct * n_nodes))")
    code.append("                end_idx = min(current_idx + count, n_nodes)")
    code.append("                for i in range(current_idx, end_idx):")
    code.append("                    self.status[nodes[i]] = self.available_statuses[status_name]")
    code.append("                current_idx = end_idx")
    code.append("        self.initial_status = self.status.copy()")
    code.append("        return self")
    code.append("")

    return "\n".join(code)


def generate_continuous_opinion_custom_model_class(
    model_data,
    class_name,
    statuses,
    compartments,
    rules,
    initial_status,
    initial_opinion_distribution,
):
    """
    Generates a Python source string for continuous opinion custom models.
    """
    opinion_params = {
        "epsilon": None,
        "gamma": None,
        "mu": None,
    }
    opinion_block_names = {
        "OpinionDistanceThreshold": None,
        "OpinionSelectionBias": None,
        "OpinionCompromise": None,
    }

    for comp in compartments:
        comp_type = comp.get("type")
        params = comp.get("params", {})
        if comp_type == "OpinionDistanceThreshold" and opinion_params["epsilon"] is None:
            opinion_params["epsilon"] = clamp_unit_float(params.get("epsilon", 0.1), 0.1)
            opinion_block_names[comp_type] = comp.get("name", "opinion_threshold")
        elif comp_type == "OpinionSelectionBias" and opinion_params["gamma"] is None:
            try:
                opinion_params["gamma"] = max(0.0, float(params.get("gamma", 0.0)))
            except (TypeError, ValueError):
                opinion_params["gamma"] = 0.0
            opinion_block_names[comp_type] = comp.get("name", "selection_bias")
        elif comp_type == "OpinionCompromise" and opinion_params["mu"] is None:
            opinion_params["mu"] = clamp_unit_float(params.get("mu", 0.5), 0.5)
            opinion_block_names[comp_type] = comp.get("name", "compromise")

    code = [
        "import numpy as np",
        "from ndlib.models.DiffusionModel import DiffusionModel",
        "from ndlib.models.opinions.initial_opinion_distribution import sample_initial_opinions",
        "",
        "class %s(DiffusionModel):" % class_name,
        "    def __init__(self, graph, seed=None):",
        "        super(%s, self).__init__(graph, seed)" % class_name,
        "        self.discrete_state = False",
        "        self.available_statuses = {'Opinion': 0}",
        "        self.parameters = {",
        "            'model': {",
        "                'initial_opinion_distribution': {",
        "                    'descr': 'Initial opinion distribution in [0, 1]',",
        "                    'choices': [",
        "                        {'value': 'uniform', 'label': 'Uniform'},",
        "                        {'value': 'normal', 'label': 'Normal'},",
        "                        {'value': 'gaussian', 'label': 'Gaussian'},",
        "                        {'value': 'bimodal', 'label': 'Bimodal'},",
        "                        {'value': 'left_skewed', 'label': 'Left skewed'},",
        "                        {'value': 'right_skewed', 'label': 'Right skewed'},",
        "                        {'value': 'polarized', 'label': 'Polarized'},",
        "                    ],",
        "                    'optional': True,",
        "                    'default': %r" % initial_opinion_distribution,
        "                },",
    ]
    if opinion_params["epsilon"] is not None:
        code.extend([
            "                'epsilon': {",
            "                    'descr': 'Opinion distance threshold (bounded confidence)',",
            "                    'range': [0, 1],",
            "                    'optional': True,",
            "                    'default': %s" % repr(float(opinion_params["epsilon"])),
            "                },",
        ])
    if opinion_params["gamma"] is not None:
        code.extend([
            "                'gamma': {",
            "                    'descr': 'Opinion selection bias',",
            "                    'range': [0, 100],",
            "                    'optional': True,",
            "                    'default': %s" % repr(float(opinion_params["gamma"])),
            "                },",
        ])
    if opinion_params["mu"] is not None:
        code.extend([
            "                'mu': {",
            "                    'descr': 'Opinion compromise strength',",
            "                    'range': [0, 1],",
            "                    'optional': True,",
            "                    'default': %s" % repr(float(opinion_params["mu"])),
            "                },",
        ])
    code.extend([
        "            },",
        "            'nodes': {},",
        "            'edges': {}",
        "        }",
        "        self.name = %r" % model_data.get("name", "CustomModel"),
        "        self.continuous_blocks = {",
        "            'distance_threshold': %r," % opinion_block_names["OpinionDistanceThreshold"],
        "            'selection_bias': %r," % opinion_block_names["OpinionSelectionBias"],
        "            'compromise': %r" % opinion_block_names["OpinionCompromise"],
        "        }",
        "",
        "    def set_initial_status(self, configuration=None):",
        "        configuration = configuration or None",
        "        model_params = configuration.get_model_parameters() if configuration is not None else {}",
        "        self.params['nodes'] = {}",
        "        self.params['edges'] = {}",
        "        self.params['status'] = {}",
        "        self.params['model'] = {}",
        "        for param, param_info in self.parameters['model'].items():",
        "            self.params['model'][param] = model_params.get(param, param_info.get('default'))",
        "        opinions = sample_initial_opinions(",
        "            len(self.status),",
        "            self.params['model'].get('initial_opinion_distribution', %r)," % initial_opinion_distribution,
        "        )",
        "        for node, opinion in zip(self.status, opinions):",
        "            self.status[node] = float(opinion)",
        "            self.graph.nodes[node]['opinion'] = float(opinion)",
        "        self.initial_status = self.status.copy()",
        "        return self",
        "",
        "    def _select_neighbor(self, node, actual_status):",
        "        neighbors = list(self.graph.neighbors(node))",
        "        if self.graph.directed:",
        "            neighbors = list(self.graph.predecessors(node))",
        "        if not neighbors:",
        "            return None",
        "        gamma = self.params['model'].get('gamma', %s)" % repr(float(opinion_params["gamma"] if opinion_params["gamma"] is not None else 0.0)),
        "        if gamma <= 0:",
        "            return neighbors[np.random.randint(0, len(neighbors))]",
        "        opinions = np.array([actual_status[neigh] for neigh in neighbors], dtype=float)",
        "        diff = np.abs(opinions - float(actual_status[node]))",
        "        weights = np.power(np.maximum(diff, 1e-5), -gamma)",
        "        total = float(np.sum(weights))",
        "        if not np.isfinite(total) or total <= 0:",
        "            return neighbors[np.random.randint(0, len(neighbors))]",
        "        weights = weights / total",
        "        return neighbors[np.random.choice(len(neighbors), p=weights)]",
        "",
        "    def iteration(self, node_status=True):",
        "        actual_status = self.status.copy()",
        "        if self.actual_iteration == 0:",
        "            self.actual_iteration += 1",
        "            if node_status:",
        "                return {'iteration': 0, 'status': actual_status.copy(), 'node_count': {}, 'status_delta': {}}",
        "            return {'iteration': 0, 'status': {}, 'node_count': {}, 'status_delta': {}}",
        "",
        "        epsilon = self.params['model'].get('epsilon', %s)" % repr(float(opinion_params["epsilon"] if opinion_params["epsilon"] is not None else 0.1)),
        "        mu = self.params['model'].get('mu', %s)" % repr(float(opinion_params["mu"] if opinion_params["mu"] is not None else 0.5)),
        "        n_nodes = max(1, self.graph.number_of_nodes())",
        "        for _ in range(n_nodes):",
        "            node = list(self.graph.nodes)[np.random.randint(0, self.graph.number_of_nodes())]",
        "            neighbor = self._select_neighbor(node, actual_status)",
        "            if neighbor is None:",
        "                continue",
        "            diff = abs(float(actual_status[node]) - float(actual_status[neighbor]))",
        "            if diff <= epsilon:",
        "                node_val = float(actual_status[node])",
        "                neigh_val = float(actual_status[neighbor])",
        "                actual_status[node] = float(np.clip(node_val + mu * (neigh_val - node_val), 0.0, 1.0))",
        "                actual_status[neighbor] = float(np.clip(neigh_val + mu * (node_val - neigh_val), 0.0, 1.0))",
        "        for node, opinion in actual_status.items():",
        "            self.graph.nodes[node]['opinion'] = float(opinion)",
        "        self.status = actual_status",
        "        self.actual_iteration += 1",
        "        if node_status:",
        "            return {'iteration': self.actual_iteration - 1, 'status': actual_status.copy(), 'node_count': {}, 'status_delta': {}}",
        "        return {'iteration': self.actual_iteration - 1, 'status': {}, 'node_count': {}, 'status_delta': {}}",
    ])

    return "\n".join(code)


def generate_ndql_script(model_data):
    """
    Generates a standard NDQL query string from custom visual model JSON data.
    """
    model_name = model_data.get("name", "CustomModel")
    statuses = model_data.get("statuses", [])
    compartments = model_data.get("compartments", [])
    rules = model_data.get("rules", [])
    initial_status = model_data.get("initial_status", [])
    continuous_opinion_mode = bool(
        model_data.get("use_case") == "continuous_opinions"
        or model_data.get("template_id") == "algorithmic_bias"
        or any(comp.get("type") in CONTINUOUS_OPINION_BLOCK_TYPES for comp in compartments)
    )

    if continuous_opinion_mode:
        ndql = []
        ndql.append("MODEL %s" % model_name)
        ndql.append("TYPE CONTINUOUS_OPINION")
        ndql.append("INITIAL_OPINION_DISTRIBUTION %s" % model_data.get("initial_opinion_distribution", "uniform"))
        ndql.append("")

        for comp in compartments:
            comp_type = comp.get("type")
            params = comp.get("params", {})
            if comp_type == "OpinionDistanceThreshold":
                ndql.append("BLOCK %s" % comp.get("name", comp_type))
                ndql.append("TYPE OpinionDistanceThreshold")
                ndql.append("PARAM epsilon %s" % params.get("epsilon", 0.1))
                ndql.append("")
            elif comp_type == "OpinionSelectionBias":
                ndql.append("BLOCK %s" % comp.get("name", comp_type))
                ndql.append("TYPE OpinionSelectionBias")
                ndql.append("PARAM gamma %s" % params.get("gamma", 0.0))
                ndql.append("")
            elif comp_type == "OpinionCompromise":
                ndql.append("BLOCK %s" % comp.get("name", comp_type))
                ndql.append("TYPE OpinionCompromise")
                ndql.append("PARAM mu %s" % params.get("mu", 0.5))
                ndql.append("")
            elif comp_type == "NodeNumericalVariable" and params.get("var") == "opinion" and params.get("var_type") == "ATTRIBUTE":
                ndql.append("BLOCK %s" % comp.get("name", comp_type))
                ndql.append("TYPE OpinionGate")
                ndql.append("PARAM variable opinion")
                ndql.append("PARAM operator %s" % params.get("op", ">="))
                ndql.append("PARAM threshold %s" % params.get("value", 0.5))
                ndql.append("")

        return "\n".join(ndql)

    ndql = []
    ndql.append("MODEL %s" % model_name)
    ndql.append("")

    for status in statuses:
        ndql.append("STATUS %s" % status["name"])
    ndql.append("")

    # Sort compartments: simple dependency sorting for ConditionalComposition
    sorted_comps = []
    pending = list(compartments)
    defined_names = set()
    
    for _ in range(10):
        if not pending:
            break
        next_pending = []
        for comp in pending:
            comp_type = comp["type"]
            params = comp.get("params", {})
            
            deps = []
            if comp_type == "ConditionalComposition":
                if params.get("condition"): deps.append(params["condition"])
                if params.get("first_branch"): deps.append(params["first_branch"])
                if params.get("second_branch"): deps.append(params["second_branch"])
            
            if all(d in defined_names for d in deps):
                sorted_comps.append(comp)
                defined_names.add(comp["name"])
            else:
                next_pending.append(comp)
        pending = next_pending
    for comp in pending:
        sorted_comps.append(comp)

    for comp in sorted_comps:
        if comp["type"] == "ConditionalComposition":
            params = comp.get("params", {})
            ndql.append("IF %s THEN %s ELSE %s AS %s" % (
                params.get("condition", ""),
                params.get("first_branch", ""),
                params.get("second_branch", ""),
                comp["name"]
            ))
            ndql.append("")
        else:
            ndql.append("COMPARTMENT %s" % comp["name"])
            ndql.append("TYPE %s" % comp["type"])
            params = comp.get("params", {})
            if comp["type"] == "NodeNumericalVariable" and params.get("var") == "opinion" and params.get("var_type") == "ATTRIBUTE":
                ndql.append("OPINION_VARIABLE opinion")
                ndql.append("OPINION_INITIALIZATION %s" % model_data.get("initial_opinion_distribution", "uniform"))
            if "triggering_status" in params:
                ndql.append("TRIGGER %s" % params["triggering_status"])
            for k, v in params.items():
                if k != "triggering_status":
                    ndql.append("PARAM %s %s" % (k, str(v)))
            ndql.append("")

    for rule in rules:
        ndql.append("RULE")
        ndql.append("FROM %s" % rule["from"])
        ndql.append("TO %s" % rule["to"])
        ndql.append("USING %s" % rule["using"])
        ndql.append("")

    ndql.append("INITIALIZE")
    for init in initial_status:
        ndql.append("SET %s %s" % (init["status"], str(init.get("ratio", 0.0))))
    ndql.append("")

    return "\n".join(ndql)


def sanitize_model_name(model_name):
    return "".join(c for c in str(model_name or "") if c.isalnum() or c == "_")


def discover_models():
    models = {}
    exclude_classes = ["DiffusionModel", "Configuration", "ConfigurationException", "ContinuousModel", "DynamicDiffusionModel"]
    epidemic_display_names = {
        "GeneralThresholdModel": "General Threshold",
        "GeneralisedThresholdModel": "Generalised Threshold",
        "KerteszThresholdModel": "Kertész Threshold",
        "SEIRctModel": "SEIR (ct)",
        "SEISctModel": "SEIS (ct)",
    }
    epidemic_group_order = {
        "Core Epidemic Models": 10,
        "Threshold and Cascade Models": 20,
        "Community-Based Models": 30,
    }
    epidemic_group_map = {
        "Core Epidemic Models": {
            "SIModel", "SISModel", "SIRModel", "SIRSModel", "SIRDModel", "SAIRModel",
            "SEIRModel", "SEIRctModel", "SEISModel", "SEISctModel", "SVEIRModel",
            "SWIRModel"
        },
        "Threshold and Cascade Models": {
            "ThresholdModel", "GeneralThresholdModel", "GeneralisedThresholdModel",
            "KerteszThresholdModel", "ProfileModel", "ProfileThresholdModel",
            "IndependentCascadesModel", "ForestFireModel", "UTLDRModel"
        },
        "Community-Based Models": {"ICEModel", "ICPModel", "ICEPModel"},
    }
    epidemic_group_rank = {name: rank for name, rank in epidemic_group_order.items()}
    opinion_display_names = {
        "AlgorithmicBiasModel": "Algorithmic Bias",
        "AlgorithmicBiasMediaModel": "Algorithmic Bias and Media",
        "ARWHKModel": "Attraction-Repulsion WHK",
        "FJModel": "Friedkin-Johnsen",
        "HKModel": "Hegselmann-Krause",
        "WHKModel": "Weighted HK",
        "AltafiniModel": "Altafini",
        "CognitiveOpDynModel": "Cognitive Opinion Dynamics",
        "MajorityRuleModel": "Majority Rule",
        "QVoterModel": "Q-Voter",
        "SznajdModel": "Sznajd",
        "VoterModel": "Voter",
        "VoterZealotModel": "Voter with Zealots",
        "NLSModel": "Nowak-Lewenstein-Szamrej",
    }
    opinion_group_order = {
        "Continuous Opinion Models": 10,
        "Discrete Opinion Models": 20,
        "Other Opinion Models": 30,
    }
    opinion_group_map = {
        "Continuous Opinion Models": {
            "AlgorithmicBiasModel", "AlgorithmicBiasMediaModel", "ARWHKModel",
            "FJModel", "HKModel", "WHKModel", "AltafiniModel", "CognitiveOpDynModel"
        },
        "Discrete Opinion Models": {
            "MajorityRuleModel", "QVoterModel", "SznajdModel", "VoterModel",
            "VoterZealotModel", "NLSModel"
        },
        "Other Opinion Models": set(),
    }
    opinion_group_rank = {name: rank for name, rank in opinion_group_order.items()}
    
    # Discover epidemics models
    for name, obj in inspect.getmembers(epd, inspect.isclass):
        if name in exclude_classes:
            continue
        try:
            g = nx.Graph()
            g.add_node(0)
            model_instance = obj(g)
            if hasattr(model_instance, "available_statuses"):
                class_name = name
                display_name = getattr(model_instance, "name", name)
                if class_name == "ICEPModel":
                    display_name = "Community Permeability (Embeddedness)"
                elif class_name == "ICPModel":
                    display_name = "Community Permeability"
                elif class_name in epidemic_display_names:
                    display_name = epidemic_display_names[class_name]

                display_group = None
                display_order = 999
                for group_name, group_members in epidemic_group_map.items():
                    if class_name in group_members:
                        display_group = group_name
                        display_order = epidemic_group_rank.get(group_name, 999)
                        break

                models[name] = {
                    "category": "Epidemics",
                    "name": display_name,
                    "class_name": class_name,
                    "parameters": model_instance.parameters,
                    "statuses": model_instance.available_statuses,
                    "discrete_state": getattr(model_instance, "discrete_state", True),
                    "display_group": display_group or "Other Epidemic Models",
                    "display_order": display_order,
                }
                if class_name in COMMUNITY_ASSIGNMENT_MODELS:
                    models[name]["requires_community_assignment"] = True
                    models[name]["community_detection_algorithms"] = COMMUNITY_DETECTION_ALGORITHMS
                    models[name]["community_detection_default"] = "louvain_communities"
        except Exception:
            pass

    # Discover opinions models
    for name, obj in inspect.getmembers(opn, inspect.isclass):
        if name in exclude_classes:
            continue
        try:
            g = nx.Graph()
            g.add_node(0)
            model_instance = obj(g)
            if hasattr(model_instance, "available_statuses"):
                display_name = getattr(model_instance, "name", name)
                if name in opinion_display_names:
                    display_name = opinion_display_names[name]

                display_group = None
                display_order = 999
                for group_name, group_members in opinion_group_map.items():
                    if name in group_members:
                        display_group = group_name
                        display_order = opinion_group_rank.get(group_name, 999)
                        break

                models[name] = {
                    "category": "Opinions",
                    "name": display_name,
                    "class_name": name,
                    "parameters": model_instance.parameters,
                    "statuses": model_instance.available_statuses,
                    "discrete_state": getattr(model_instance, "discrete_state", True),
                    "display_group": display_group or "Other Opinion Models",
                    "display_order": display_order,
                }
        except Exception:
            pass

    # Discover custom models from the custom_models package
    custom_dir = os.path.join(os.path.dirname(__file__), "custom_models")
    if os.path.exists(custom_dir):
        if custom_dir not in sys.path:
            sys.path.insert(0, os.path.dirname(custom_dir))

        for f_name in os.listdir(custom_dir):
            if f_name.endswith(".py") and not f_name.startswith("__"):
                module_name = f_name[:-3]
                try:
                    full_module_name = "ndlib.dashboard.custom_models.%s" % module_name
                    if full_module_name in sys.modules:
                        importlib.reload(sys.modules[full_module_name])
                        mod = sys.modules[full_module_name]
                    else:
                        mod = importlib.import_module(full_module_name)
                    
                    for name, obj in inspect.getmembers(mod, inspect.isclass):
                        if name == module_name:
                            g = nx.Graph()
                            g.add_node(0)
                            model_instance = obj(g)
                            models[name] = {
                                "category": "Custom Models",
                                "name": getattr(model_instance, "name", name),
                                "class_name": name,
                                "parameters": model_instance.parameters,
                                "statuses": model_instance.available_statuses,
                                "discrete_state": getattr(model_instance, "discrete_state", True),
                                "is_custom": True
                            }
                except Exception as e:
                    print("Warning: failed to load custom model %s: %s" % (module_name, str(e)))
                    pass

    return sanitize_for_json(models)


class DashboardRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence default requests logging to stdout to keep terminal clean
        pass

    def end_headers(self):
        # Enable CORS for development
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        try:
            # API endpoints
            if self.path == "/api/models":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                try:
                    models = discover_models()
                    self.wfile.write(json.dumps(models).encode("utf-8"))
                except Exception as e:
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            if self.path == "/api/custom-models":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                try:
                    custom_dir = os.path.join(os.path.dirname(__file__), "custom_models")
                    models_meta = []
                    if os.path.exists(custom_dir):
                        for f_name in os.listdir(custom_dir):
                            if f_name.endswith(".json"):
                                with open(os.path.join(custom_dir, f_name), "r") as f:
                                    models_meta.append(json.load(f))
                    self.wfile.write(json.dumps(models_meta).encode("utf-8"))
                except Exception as e:
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            if self.path.startswith("/api/custom-models/download"):
                parsed = urlparse(self.path)
                query = parse_qs(parsed.query)
                model_name = query.get("name", [""])[0]
                safe_name = sanitize_model_name(model_name)
                if not safe_name:
                    raise ValueError("Model name is required")

                custom_dir = os.path.join(os.path.dirname(__file__), "custom_models")
                py_path = os.path.join(custom_dir, safe_name + ".py")
                if not os.path.exists(py_path):
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Python file not found"}).encode("utf-8"))
                    return

                with open(py_path, "rb") as f:
                    py_bytes = f.read()

                self.send_response(200)
                self.send_header("Content-type", "text/x-python; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="%s.py"' % safe_name)
                self.send_header("Content-Length", str(len(py_bytes)))
                self.end_headers()
                self.wfile.write(py_bytes)
                return

            # Serve static files
            clean_path = self.path.split("?")[0]
            if clean_path == "/" or clean_path == "":
                file_path = os.path.join(FRONTEND_DIR, "index.html")
            else:
                file_path = os.path.join(FRONTEND_DIR, clean_path.lstrip("/"))

            if os.path.exists(file_path) and not os.path.isdir(file_path):
                self.send_response(200)
                # Guess MIME type
                if file_path.endswith(".html"):
                    self.send_header("Content-type", "text/html")
                elif file_path.endswith(".js"):
                    self.send_header("Content-type", "application/javascript")
                elif file_path.endswith(".css"):
                    self.send_header("Content-type", "text/css")
                elif file_path.endswith(".png"):
                    self.send_header("Content-type", "image/png")
                elif file_path.endswith(".svg"):
                    self.send_header("Content-type", "image/svg+xml")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                # SPA fallback to index.html
                fallback_index = os.path.join(FRONTEND_DIR, "index.html")
                if os.path.exists(fallback_index):
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    with open(fallback_index, "rb") as f:
                        self.wfile.write(f.read())
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Frontend assets not found. Run frontend build first.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            try:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
            except Exception:
                pass

    def do_POST(self):
        if self.path == "/api/custom-models/save":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            try:
                model_name = payload.get("name")
                if not model_name:
                    raise ValueError("Model name is required")
                
                safe_name = sanitize_model_name(model_name)
                if not safe_name:
                    raise ValueError("Invalid model name")
                
                custom_dir = os.path.join(os.path.dirname(__file__), "custom_models")
                if not os.path.exists(custom_dir):
                    os.makedirs(custom_dir)
                
                # Save visual layout JSON
                json_path = os.path.join(custom_dir, safe_name + ".json")
                with open(json_path, "w") as f:
                    json.dump(payload, f, indent=4)
                
                # Generate NDQL query
                ndql_query = generate_ndql_script(payload)
                ndql_path = os.path.join(custom_dir, safe_name + ".ndql")
                with open(ndql_path, "w") as f:
                    f.write(ndql_query)
                
                # Generate Python class code
                class_code = generate_custom_model_class(payload)
                py_path = os.path.join(custom_dir, safe_name + ".py")
                with open(py_path, "w") as f:
                    f.write(class_code)
                
                # Force dynamic import / reload
                full_module_name = "ndlib.dashboard.custom_models.%s" % safe_name
                if full_module_name in sys.modules:
                    importlib.reload(sys.modules[full_module_name])
                else:
                    importlib.import_module(full_module_name)
                
                self.wfile.write(json.dumps({
                    "success": True,
                    "model_name": model_name,
                    "safe_name": safe_name,
                    "python_filename": "%s.py" % safe_name,
                    "download_url": "/api/custom-models/download?name=%s" % safe_name
                }).encode("utf-8"))
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        elif self.path == "/api/custom-models/delete":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))
            model_name = payload.get("name")
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            try:
                if not model_name:
                    raise ValueError("Model name is required")
                custom_dir = os.path.join(os.path.dirname(__file__), "custom_models")
                safe_name = sanitize_model_name(model_name)
                for ext in [".json", ".ndql", ".py"]:
                    f_path = os.path.join(custom_dir, safe_name + ext)
                    if os.path.exists(f_path):
                        os.remove(f_path)
                
                mod_name = "ndlib.dashboard.custom_models.%s" % safe_name
                if mod_name in sys.modules:
                    del sys.modules[mod_name]
                    
                self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        if self.path in {"/api/network", "/api/simulate"}:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            try:
                graph_data = payload.get("graph_data")
                if graph_data:
                    g = build_graph_from_serialized(graph_data)
                    graph_meta = serialize_graph_for_frontend(g)
                else:
                    graph_type = payload.get("graph_type", "erdos_renyi")
                    graph_params = payload.get("graph_params", {})
                    g = build_graph_from_payload(graph_type, graph_params)
                    graph_meta = serialize_graph_for_frontend(g)

                if self.path == "/api/network":
                    response = {
                        **graph_meta,
                        "graph_type": payload.get("graph_type", "erdos_renyi"),
                        "graph_params": payload.get("graph_params", {}),
                    }
                    self.wfile.write(json.dumps(response).encode("utf-8"))
                    return

                # 2. Select Model Class
                model_class_name = payload.get("model_class")
                category = payload.get("category", "Epidemics")

                if category == "Epidemics":
                    model_class = resolve_model_class(category, model_class_name)
                else:
                    model_class = resolve_model_class(category, model_class_name)

                model_instance = model_class(g)

                # 3. Apply Configuration Parameters
                cfg = mc.Configuration()
                model_params = payload.get("model_params", {})
                selected_seed_nodes = [
                    deserialize_node_id(node_id)
                    for node_id in payload.get("selected_seed_nodes", [])
                    if node_id is not None and str(node_id) != ""
                ]
                initial_status_percentages = model_params.get("initial_status_percentages", {})
                zealot_percentage = model_params.get("zealot_percentage", None)
                community_detection_algorithm = model_params.get(
                    "community_detection_algorithm",
                    getattr(model_instance, "community_detection_default", "louvain_communities"),
                )
                community_detection_k = model_params.get("community_detection_k", 2)

                for param, val in model_params.items():
                    if param in {
                        "community_detection_algorithm",
                        "community_detection_k",
                        "initial_status_percentages",
                        "zealot_percentage",
                    }:
                        continue

                    # Handle typing
                    p_info = {}
                    if param in model_instance.parameters["model"]:
                        p_info = model_instance.parameters["model"][param]
                    elif param in model_instance.parameters["nodes"]:
                        p_info = model_instance.parameters["nodes"][param]
                    elif param in model_instance.parameters["edges"]:
                        p_info = model_instance.parameters["edges"][param]

                    if param == "percentage_infected":
                        if category == "Epidemics" and selected_seed_nodes:
                            continue
                        # Dashboard percent input is 0-100; NDLib expects a fraction.
                        val = float(val) / 100.0
                    elif p_info:
                        val = coerce_model_parameter_value(param, val, p_info)

                    if param in model_instance.parameters["model"] or param == "percentage_infected":
                        cfg.add_model_parameter(param, val)
                    elif param in model_instance.parameters["nodes"]:
                        for n in g.nodes():
                            cfg.add_node_configuration(param, n, val)
                    elif param in model_instance.parameters["edges"]:
                        for e in g.edges():
                            cfg.add_edge_configuration(param, e, val)

                if category == "Opinions" and getattr(model_instance, "discrete_state", True):
                    if isinstance(initial_status_percentages, dict) and initial_status_percentages:
                        assignment = build_initial_status_assignment(
                            g,
                            model_instance.available_statuses,
                            initial_status_percentages,
                        )
                        grouped_nodes = {}
                        for node, status_name in assignment.items():
                            grouped_nodes.setdefault(status_name, []).append(node)
                        for status_name, nodes in grouped_nodes.items():
                            cfg.add_model_initial_configuration(status_name, nodes)

                # Apply initial infection state if provided and relevant
                if (
                    "fraction_infected" in model_instance.parameters["model"]
                    and "fraction_infected" not in model_params
                    and not selected_seed_nodes
                ):
                    cfg.add_model_parameter("fraction_infected", 0.05)

                if category == "Epidemics" and selected_seed_nodes:
                    infected_nodes = [node for node in selected_seed_nodes if node in g.nodes()]
                    if infected_nodes:
                        cfg.add_model_initial_configuration("Infected", infected_nodes)
                elif model_class_name == "VoterZealotModel":
                    zealot_nodes = [node for node in selected_seed_nodes if node in g.nodes()]
                    if not zealot_nodes and zealot_percentage is not None:
                        try:
                            zealot_fraction = max(0.0, min(100.0, float(zealot_percentage))) / 100.0
                        except (TypeError, ValueError):
                            zealot_fraction = 0.0
                        num_zealots = int(round(g.number_of_nodes() * zealot_fraction))
                        if zealot_fraction > 0 and num_zealots == 0:
                            num_zealots = 1
                        num_zealots = min(g.number_of_nodes(), max(0, num_zealots))
                        if num_zealots > 0:
                            zealot_nodes = list(np.random.choice(list(g.nodes()), num_zealots, replace=False))
                    if zealot_nodes:
                        for node in g.nodes():
                            cfg.add_node_configuration("zealot", node, 1 if node in zealot_nodes else 0)

                # Community-based models need node communities assigned.
                if needs_community_assignment(model_instance):
                    node_cfg = cfg.get_nodes_configuration()
                    if "com" not in node_cfg:
                        community_map = build_community_assignment_with_algorithm(
                            g,
                            algorithm=community_detection_algorithm,
                            k=community_detection_k,
                        )
                        for node, community_id in community_map.items():
                            cfg.add_node_configuration("com", node, community_id)

                model_instance.set_initial_status(cfg)

                # 4. Execute Simulation
                num_iterations = int(payload.get("iterations", 100))
                iterations = model_instance.iteration_bunch(num_iterations)

                # Format iterations to handle potential non-serializable objects (like sets)
                formatted_iterations = []
                for it in iterations:
                    it = normalize_iteration_record(it)

                    node_count_clean = normalize_iteration_counts(
                        it.get("node_count", {}), model_instance.available_statuses
                    )

                    status_delta = it.get("status_delta", {})
                    if isinstance(status_delta, dict):
                        status_delta_clean = {
                            str(k): (
                                float(v) if isinstance(v, (float, np.floating)) else int(v)
                            )
                            for k, v in status_delta.items()
                        }
                    else:
                        status_delta_clean = normalize_iteration_counts(
                            status_delta, model_instance.available_statuses
                        )

                    iteration_id = int(it.get("iteration", len(formatted_iterations)))
                    formatted_iterations.append({
                        "iteration": iteration_id,
                        "status": {
                            str(k): (
                                float(v) if isinstance(v, (float, np.floating)) else int(v)
                            )
                            for k, v in it["status"].items()
                        },
                        "node_count": node_count_clean,
                        "status_delta": status_delta_clean
                    })

                discrete_state = getattr(model_instance, "discrete_state", True)
                absolute_status_history = build_absolute_status_history(
                    formatted_iterations,
                    graph_meta.get("nodes", []),
                )
                response = {
                    "iterations": formatted_iterations,
                    **graph_meta,
                    "statuses": model_instance.available_statuses,
                    "discrete_state": discrete_state,
                    "is_continuous": not discrete_state,
                    "absolute_status_history": absolute_status_history,
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))

            except Exception as e:
                import traceback
                traceback.print_exc()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))


def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def main():
    global PORT
    # Check if port 5000 is taken, otherwise find a free port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", PORT))
        s.close()
    except socket.error:
        PORT = find_free_port()

    server_address = ("127.0.0.1", PORT)
    httpd = http.server.ThreadingHTTPServer(server_address, DashboardRequestHandler)
    print("==================================================")
    print("  NDlib Interactive Dashboard Server running")
    print("  URL: http://127.0.0.1:%s" % PORT)
    print("  Press Ctrl+C to stop.")
    print("==================================================")

    # Automatically open web browser
    webbrowser.open("http://127.0.0.1:%s" % PORT)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


if __name__ == "__main__":
    main()
