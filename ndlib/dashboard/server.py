import http.server
import importlib
import json
import os
import sys
import webbrowser
import socket
import inspect
import numpy as np
import networkx as nx
from networkx.algorithms import community as nx_community

# Add the repository root to the front of the import path so the dashboard
# always uses the source tree currently being edited, not an installed copy.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)
for module_name in list(sys.modules):
    if module_name == "ndlib" or module_name.startswith("ndlib."):
        del sys.modules[module_name]

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

    if is_threshold_parameter(param, p_info) or range_info == [0, 1]:
        return clamp_unit_float(val, p_info.get("default", 0.1))

    if isinstance(default_val, float) or range_info == [0, 1] or range_info == [-1, 1]:
        return float(val)

    if range_info is float:
        return float(val)

    if param in int_params:
        return max(1, int(round(float(val))))

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
    Resolve a model class from the local source tree.

    Some environments preload a different ``ndlib`` installation whose package
    namespace may not match the repository under test. Importing the concrete
    module path first keeps the dashboard aligned with the source tree.
    """
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
    httpd = http.server.HTTPServer(server_address, DashboardRequestHandler)
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
