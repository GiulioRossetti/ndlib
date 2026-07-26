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

    # Coerce to integer if default value is an integer or param is known to be int
    if (isinstance(default_val, int) and not isinstance(default_val, bool)) or param in int_params:
        try:
            return max(1, int(round(float(val))))
        except (ValueError, TypeError):
            try:
                return max(1, int(val))
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


def generate_ndql_script(model_data):
    """
    Generates a standard NDQL query string from custom visual model JSON data.
    """
    model_name = model_data.get("name", "CustomModel")
    statuses = model_data.get("statuses", [])
    compartments = model_data.get("compartments", [])
    rules = model_data.get("rules", [])
    initial_status = model_data.get("initial_status", [])

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

                models[name] = {
                    "category": "Epidemics",
                    "name": display_name,
                    "class_name": class_name,
                    "parameters": model_instance.parameters,
                    "statuses": model_instance.available_statuses,
                    "discrete_state": getattr(model_instance, "discrete_state", True)
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
                models[name] = {
                    "category": "Opinions",
                    "name": getattr(model_instance, "name", name),
                    "class_name": name,
                    "parameters": model_instance.parameters,
                    "statuses": model_instance.available_statuses,
                    "discrete_state": getattr(model_instance, "discrete_state", True)
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
                community_detection_algorithm = model_params.get(
                    "community_detection_algorithm",
                    getattr(model_instance, "community_detection_default", "louvain_communities"),
                )
                community_detection_k = model_params.get("community_detection_k", 2)

                for param, val in model_params.items():
                    if param in {"community_detection_algorithm", "community_detection_k"}:
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

                    formatted_iterations.append({
                        "iteration": int(it["iteration"]),
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
                response = {
                    "iterations": formatted_iterations,
                    **graph_meta,
                    "statuses": model_instance.available_statuses,
                    "discrete_state": discrete_state,
                    "is_continuous": not discrete_state
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
