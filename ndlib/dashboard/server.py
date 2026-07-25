import http.server
import json
import os
import sys
import webbrowser
import socket
import inspect
import numpy as np
import networkx as nx

# Add parent directory to path to ensure ndlib imports work
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import ndlib.models.epidemics as epd
import ndlib.models.opinions as opn
import ndlib.models.ModelConfig as mc

__author__ = "Antigravity"
__license__ = "BSD-2-Clause"

PORT = 5000
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "dist")


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
                models[name] = {
                    "category": "Epidemics",
                    "name": getattr(model_instance, "name", name),
                    "class_name": name,
                    "parameters": model_instance.parameters,
                    "statuses": model_instance.available_statuses
                }
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
                    "statuses": model_instance.available_statuses
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
        if self.path == "/api/simulate":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            try:
                # 1. Load or Generate Graph
                graph_type = payload.get("graph_type", "erdos_renyi")
                graph_params = payload.get("graph_params", {})

                if graph_type == "erdos_renyi":
                    g = nx.erdos_renyi_graph(
                        int(graph_params.get("n", 100)),
                        float(graph_params.get("p", 0.1))
                    )
                elif graph_type == "barabasi_albert":
                    g = nx.barabasi_albert_graph(
                        int(graph_params.get("n", 100)),
                        int(graph_params.get("m", 2))
                    )
                elif graph_type == "watts_strogatz":
                    g = nx.watts_strogatz_graph(
                        int(graph_params.get("n", 100)),
                        int(graph_params.get("k", 4)),
                        float(graph_params.get("p", 0.1))
                    )
                elif graph_type == "complete":
                    g = nx.complete_graph(int(graph_params.get("n", 100)))
                elif graph_type == "upload":
                    content = graph_params.get("file_content", "")
                    fmt = graph_params.get("file_format", "graphml")
                    if fmt == "graphml":
                        g = nx.parse_graphml(content)
                    elif fmt == "gml":
                        g = nx.parse_gml(content)
                    else:
                        # Edgelist fallback
                        g = nx.parse_edgelist(content.splitlines())
                else:
                    raise ValueError("Unknown graph type: %s" % graph_type)

                # Convert to directed if graph_params says so
                if graph_params.get("directed", False):
                    g = g.to_directed()

                # 2. Select Model Class
                model_class_name = payload.get("model_class")
                category = payload.get("category", "Epidemics")

                if category == "Epidemics":
                    model_class = getattr(epd, model_class_name)
                else:
                    model_class = getattr(opn, model_class_name)

                model_instance = model_class(g)

                # 3. Apply Configuration Parameters
                cfg = mc.Configuration()
                model_params = payload.get("model_params", {})

                for param, val in model_params.items():
                    # Handle typing
                    p_info = {}
                    if param in model_instance.parameters["model"]:
                        p_info = model_instance.parameters["model"][param]
                    elif param in model_instance.parameters["nodes"]:
                        p_info = model_instance.parameters["nodes"][param]
                    elif param in model_instance.parameters["edges"]:
                        p_info = model_instance.parameters["edges"][param]

                    if p_info:
                        # Convert value to correct type based on range/metadata
                        if p_info.get("range") == [0, 1] or isinstance(val, float):
                            val = float(val)
                        elif isinstance(val, int):
                            val = int(val)

                    if param in model_instance.parameters["model"]:
                        cfg.add_model_parameter(param, val)
                    elif param in model_instance.parameters["nodes"]:
                        for n in g.nodes():
                            cfg.add_node_configuration(param, n, val)
                    elif param in model_instance.parameters["edges"]:
                        for e in g.edges():
                            cfg.add_edge_configuration(param, e, val)

                # Apply initial infection state if provided and relevant
                if "fraction_infected" in model_instance.parameters["model"] and "fraction_infected" not in model_params:
                    cfg.add_model_parameter("fraction_infected", 0.05)

                model_instance.set_initial_status(cfg)

                # 4. Execute Simulation
                num_iterations = int(payload.get("iterations", 100))
                iterations = model_instance.iteration_bunch(num_iterations)

                # 5. Build Graph Nodes & Layout for frontend rendering
                pos = nx.spring_layout(g)
                nodes_data = []
                for n in g.nodes():
                    nodes_data.append({
                        "id": str(n),
                        "label": str(n),
                        "x": float(pos[n][0] * 500),
                        "y": float(pos[n][1] * 500),
                    })
                edges_data = []
                for u, v in g.edges():
                    edges_data.append({
                        "source": str(u),
                        "target": str(v)
                    })

                # Format iterations to handle potential non-serializable objects (like sets)
                formatted_iterations = []
                for it in iterations:
                    formatted_iterations.append({
                        "iteration": int(it["iteration"]),
                        "status": {str(k): int(v) for k, v in it["status"].items()},
                        "node_count": {str(k): int(v) for k, v in it["node_count"].items()},
                        "status_delta": {str(k): int(v) for k, v in it["status_delta"].items()}
                    })

                response = {
                    "iterations": formatted_iterations,
                    "nodes": nodes_data,
                    "edges": edges_data,
                    "statuses": model_instance.available_statuses
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
