try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys
import json
import os.path
import re
import networkx as nx
from ndlib.models.CompositeModel import CompositeModel

__author__ = "Giulio Rossetti"
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class ExperimentParser(object):
    def __init__(self):
        self.imports = (
            "import networkx as nx\n"
            "import numpy as np\n"
            "import json\n"
            "from ndlib.models.ModelConfig import Configuration\n"
            "from ndlib.models.CompositeModel import CompositeModel\n"
            "from ndlib.models.compartments.NodeStochastic import NodeStochastic\n"
            "from ndlib.models.compartments.NodeThreshold import NodeThreshold\n"
            "from ndlib.models.compartments.NodeCategoricalAttribute import NodeCategoricalAttribute\n"
            "from ndlib.models.compartments.NodeNumericalAttribute import NodeNumericalAttribute\n"
            "from ndlib.models.compartments.EdgeStochastic import EdgeStochastic\n"
            "from ndlib.models.compartments.EdgeCategoricalAttribute import EdgeCategoricalAttribute\n"
            "from ndlib.models.compartments.EdgeNumericalAttribute import EdgeNumericalAttribute\n"
            "from ndlib.models.compartments.ConditionalComposition import ConditionalComposition\n"
            "from ndlib.models.compartments.CountDown import CountDown\n"
        )

        self.script = ""
        self.starting = (
            "STATUS",
            "MODEL",
            "COMPARTMENT",
            "RULE",
            "IF",
            "INITIALIZE",
            "CREATE_NETWORK",
            "LOAD_NETWORK",
            "EXECUTE",
        )
        self.__model_name = None
        self.__net_name = None
        self.query = None
        self.__statuses = {}
        self.__compartments = {}
        self.__continuous_mode = False
        self.__continuous_payload = None
        self.__continuous_network_stmt = None
        self.__continuous_execution_stmt = None
        self.model = CompositeModel(nx.Graph())

    def read_query_file(self, filename):
        with open(filename) as f:
            self.query = f.read()

    def set_query(self, query):
        self.query = query

    def parse(self):
        self.script = ""
        self.__continuous_mode = False
        self.__continuous_payload = None
        self.__continuous_network_stmt = None
        self.__continuous_execution_stmt = None
        self.__statuses = {}
        self.__compartments = {}
        self.__model_name = None
        self.__net_name = None

        if self.query is None:
            raise ValueError("Experiment description malformed (empty query): check your syntax")

        if (
            "TYPE CONTINUOUS_OPINION" in self.query
            or "INITIAL_OPINION_DISTRIBUTION" in self.query
            or "BLOCK " in self.query
            or "BIN " in self.query
            or "DECLARE " in self.query
            or "OBSERVE " in self.query
        ):
            self.__parse_continuous_query()
            return

        # Tokenizing directives
        identified_directives = {}
        cmd = []
        bucket = []
        lines = self.query.split("\n")
        for line in lines:
            # Comment handling
            if len(line) == 0 or line[0] == "#":
                continue

            line = self.__sanitize_string(line)
            kwd = line.rstrip().split(" ")[0]

            if kwd in self.starting:
                identified_directives[kwd] = None
                if len(bucket) > 0:
                    cmd.append(bucket)
                bucket = [line.rstrip()]
            else:
                line = line.rstrip()
                if len(line) > 0:
                    bucket.append(line.rstrip())
        cmd.append(bucket)

        # Query consistency checks
        self.__check_components(identified_directives)

        # Lookup directives: script generation and execution
        for statement in cmd:
            key = statement[0].rstrip().split(" ")[0]

            if key == "MODEL":
                code = self.__model_creation(statement)

            elif key == "STATUS":
                code = self.__status_definition(statement)

            elif key == "COMPARTMENT":
                code = self.__compartment_definition(statement)

            elif key == "RULE":
                code = self.__rule_definition(statement)

            elif key == "IF":
                code = self.__conditional_compartment_composition(statement)

            elif key == "INITIALIZE":
                code = self.__model_configuration(statement)

            elif key == "CREATE_NETWORK":
                code = self.__network_generation(statement)

            elif key == "LOAD_NETWORK":
                code = self.__network_loading(statement)

            elif key == "EXECUTE":
                code = self.__execution_statement(statement)

            else:
                raise ValueError(
                    "The keyword '%s' is not defined: check your syntax" % key
                )
            self.script = "%s%s" % (self.script, code)

        self.__clean_imports()
        self.script = "%s\n%s" % (self.imports, self.script)

    def __parse_continuous_query(self):
        from ndlib.dashboard.server import generate_custom_model_class

        lines = self.query.split("\n")
        model_name = None
        initial_opinion_distribution = "uniform"
        statuses = []
        compartments = []
        rules = []
        initial_status = []
        declarations = []
        observables = []
        current_block = None
        current_rule = {}
        network_lines = []
        execution_line = None
        mode = None

        for raw_line in lines:
            if len(raw_line) == 0 or raw_line[0] == "#":
                continue
            line = self.__sanitize_string(raw_line).strip()
            if not line:
                continue

            parts = line.split()
            head = parts[0]

            if head == "MODEL":
                if len(parts) < 2:
                    raise ValueError("Experiment description malformed (missing model name): check your syntax")
                model_name = parts[1]
                continue
            if head == "TYPE" and len(parts) >= 2 and parts[1] == "CONTINUOUS_OPINION":
                self.__continuous_mode = True
                continue
            if head in {"INITIAL_OPINION_DISTRIBUTION", "SET"} and len(parts) >= 2:
                if head == "INITIAL_OPINION_DISTRIBUTION":
                    initial_opinion_distribution = parts[1]
                elif len(parts) >= 3 and parts[1] == "INITIAL_OPINION_DISTRIBUTION":
                    initial_opinion_distribution = parts[2]
                continue
            if head in {"BIN", "STATUS"} and len(parts) >= 2:
                status_name = parts[1]
                if status_name not in [s["name"] for s in statuses]:
                    statuses.append({"name": status_name, "code": len(statuses)})
                continue
            if head == "BLOCK":
                if len(parts) < 2:
                    raise ValueError("Experiment description malformed (missing block name): check your syntax")
                current_block = {"name": parts[1], "type": None, "params": {}}
                compartments.append(current_block)
                mode = "block"
                continue
            if head == "DECLARE":
                if len(parts) < 3:
                    raise ValueError("Experiment description malformed (wrong declaration statement): check your syntax")
                declaration = {"kind": parts[1], "name": parts[2]}
                idx = 3
                while idx < len(parts):
                    token = parts[idx]
                    if token in {"TYPE", "RANGE", "VALUES", "DEFAULT", "SCOPE"} and idx + 1 < len(parts):
                        declaration[token.lower()] = self.__coerce_ndql_value(parts[idx + 1])
                        idx += 2
                    else:
                        idx += 1
                declarations.append(declaration)
                continue
            if head == "OBSERVE":
                if len(parts) < 2:
                    raise ValueError("Experiment description malformed (wrong observe statement): check your syntax")
                observable = {"variable": parts[1]}
                idx = 2
                while idx < len(parts):
                    token = parts[idx]
                    if token == "AS" and idx + 1 < len(parts):
                        observable["mode"] = parts[idx + 1]
                        idx += 2
                    elif token in {"BINS", "RANGE", "MODE"} and idx + 1 < len(parts):
                        observable[token.lower()] = self.__coerce_ndql_value(parts[idx + 1])
                        idx += 2
                    else:
                        idx += 1
                observables.append(observable)
                continue
            if head == "TYPE" and mode == "block" and current_block is not None:
                if len(parts) < 2:
                    raise ValueError("Experiment description malformed (missing block type): check your syntax")
                current_block["type"] = parts[1]
                continue
            if head == "PARAM" and current_block is not None:
                if len(parts) < 3:
                    raise ValueError("Experiment description malformed (wrong parameter statement): check your syntax")
                param_name = parts[1]
                param_value = " ".join(parts[2:])
                current_block["params"][param_name] = self.__coerce_ndql_value(param_value)
                continue
            if head == "TRIGGER" and current_block is not None:
                if len(parts) < 2:
                    raise ValueError("Experiment description malformed (wrong trigger statement): check your syntax")
                current_block["params"]["triggering_status"] = parts[1]
                continue
            if head == "RULE":
                current_rule = {}
                mode = "rule"
                continue
            if head in {"FROM", "TO", "USING"} and mode == "rule":
                if len(parts) < 2:
                    raise ValueError("Experiment description malformed (wrong rule statement): check your syntax")
                current_rule[head.lower()] = parts[1]
                continue
            if head == "INITIALIZE":
                mode = "init"
                continue
            if head == "SET" and mode == "init" and len(parts) >= 3:
                if parts[1] == "INITIAL_OPINION_DISTRIBUTION":
                    initial_opinion_distribution = parts[2]
                else:
                    initial_status.append({"status": parts[1], "ratio": float(parts[2])})
                continue
            if head == "CREATE_NETWORK":
                network_lines.append(line)
                mode = "network"
                continue
            if head == "LOAD_NETWORK":
                network_lines.append(line)
                mode = "network"
                continue
            if head == "EXECUTE":
                execution_line = line
                continue

        for comp in compartments:
            if not comp.get("type"):
                raise ValueError("Experiment description malformed (block type missing): check your syntax")

        if model_name is None:
            raise ValueError("Experiment description malformed (Model not specified): check your syntax")

        payload = {
            "name": model_name,
            "use_case": "continuous_opinions",
            "template_id": "algorithmic_bias",
            "initial_opinion_distribution": initial_opinion_distribution,
            "statuses": statuses,
            "compartments": compartments,
            "rules": rules,
            "initial_status": initial_status,
            "declarations": declarations,
            "observables": observables,
        }

        class_code = generate_custom_model_class(payload)
        self.__continuous_payload = payload
        self.__continuous_network_stmt = network_lines[0] if network_lines else None
        self.__continuous_execution_stmt = execution_line
        self.script = class_code + "\n"
        self.script += "import networkx as nx\n"
        self.script += "import json\n"
        self.script += "from ndlib.models.ModelConfig import Configuration\n"
        if self.__continuous_network_stmt:
            self.script += self.__translate_network_statement(self.__continuous_network_stmt)
        else:
            self.script += "g1 = nx.erdos_renyi_graph(20, 0.2)\n"
        self.script += "%s_model = %s(g1)\n" % (model_name.lower(), model_name)
        self.script += "config = Configuration()\n"
        if initial_status:
            for st in initial_status:
                self.script += "config.add_model_parameter('percentage_%s', %s)\n" % (st["status"], st["ratio"])
        self.script += "%s_model.set_initial_status(config)\n" % model_name.lower()
        if self.__continuous_execution_stmt:
            exec_parts = self.__continuous_execution_stmt.split()
            if len(exec_parts) >= 6:
                self.script += "iterations = %s_model.iteration_bunch(%s)\n" % (model_name.lower(), exec_parts[5])
            else:
                self.script += "iterations = %s_model.iteration_bunch(10)\n" % model_name.lower()
        else:
            self.script += "iterations = %s_model.iteration_bunch(10)\n" % model_name.lower()
        self.script += "res = json.dumps(iterations)\nprint(res)\n"

    @staticmethod
    def __coerce_ndql_value(value):
        value = value.strip()
        if not value:
            return value
        if value.lower() in {"none", "null"}:
            return None
        if value.startswith("[") and value.endswith("]"):
            items = [x.strip() for x in value[1:-1].split(",") if x.strip()]
            return [ExperimentParser.__coerce_ndql_value(x) for x in items]
        try:
            if any(ch in value for ch in [".", "e", "E"]):
                return float(value)
            return int(value)
        except ValueError:
            return value

    @staticmethod
    def __translate_network_statement(stmt):
        parts = stmt.split()
        if not parts:
            return ""
        if parts[0] == "CREATE_NETWORK" and len(parts) >= 2:
            net_name = parts[1]
            net_type = "erdos_renyi_graph"
            params = []
            return "%s = nx.%s()\n" % (net_name, net_type)
        if parts[0] == "LOAD_NETWORK" and len(parts) == 4 and parts[2] == "FROM":
            return "g1 = nx.read_edgelist(%r)\n" % parts[3]
        return ""

    def execute_query(self):
        # Query execution
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()

        try:
            exec(self.script, locals(), globals())
        except SyntaxError:
            raise ValueError(
                "Experiment description malformed (Incorrect statement ordering): check your syntax"
            )

        sys.stdout = old_stdout
        result = json.loads(redirected_output.getvalue())
        if self.__continuous_mode:
            return result
        trends = self.model.build_trends(result)
        trends[0]["Statuses"] = {
            str(v): k for k, v in self.model.available_statuses.items()
        }
        return trends

    def __clean_imports(self):

        libs = self.imports.split("\n")
        new_imports = "\n".join(libs[:5])
        compartments = set(self.__compartments.values())
        rs = ["\\b%s\\b " % x for x in compartments]
        cps = r"|".join(rs)

        for lib in libs[5:]:
            r = re.compile(cps, flags=re.I | re.X)
            match = r.findall(lib)
            if match:
                new_imports += "\n%s\n" % lib
        self.imports = new_imports

    def __status_definition(self, desc):
        if len(desc) > 1:
            raise ValueError(
                "Experiment description malformed (wrong status definition statement): check your syntax"
            )
        part = desc[0].split(" ")
        if part[0] != "STATUS":
            raise ValueError(
                "Experiment description malformed (wrong status definition statement): check your syntax"
            )

        self.__statuses[part[1].lower()] = None
        self.model.add_status(part[1])

        return "%s.add_status('%s')\n" % (self.__model_name, part[1])

    def __execution_statement(self, desc):

        if len(desc) > 1:
            raise ValueError(
                "Experiment description malformed (wrong execution statement): check your syntax"
            )
        part = desc[0].split(" ")
        if part[0] != "EXECUTE" or part[2] != "ON" or part[4] != "FOR":
            raise ValueError(
                "Experiment description malformed (wrong execution statement): check your syntax"
            )

        if self.__model_name != part[1]:
            raise ValueError(
                "Execution Definition Error: model '%s' not defined" % part[1]
            )

        if self.__net_name != part[3]:
            raise ValueError(
                "Execution Definition Error: graph '%s' not defined" % part[3]
            )

        return (
            "iterations = %s.iteration_bunch(%s, node_status=False)\n"
            "res = json.dumps(iterations)\n"
            "print(res)\n" % (self.__model_name, part[5])
        )

    def __network_generation(self, desc):

        components = {"CREATE_NETWORK": None, "TYPE": None, "PARAM": []}

        for part in desc:
            part = part.split(" ")
            if part[0] not in components:
                raise ValueError("Unsupported description")
            if part[0] == "PARAM":
                if len(part[0]) < 3:
                    raise ValueError(
                        "Experiment description malformed (wrong network definition): check your syntax"
                    )
                else:
                    components["PARAM"].append((part[1], part[2]))
            else:
                components[part[0]] = part[1]
        self.__net_name = components["CREATE_NETWORK"]
        parameters = ""
        for pr in components["PARAM"]:
            parameters += "%s=%s, " % (pr[0], pr[1])
        code = "%s = nx.%s(%s)\n" % (self.__net_name, components["TYPE"], parameters)

        return code.replace(", )", ")")

    def __network_loading(self, desc):

        compartments = ["LOAD_NETWORK", "FROM"]

        if len(desc) > 1:
            raise ValueError("Unsupported description")
        stm = desc[0].split(" ")
        if len(stm) != 4 or stm[0] not in compartments or stm[2] not in compartments:
            raise ValueError(
                "Experiment description malformed (wrong network loading statement): check your syntax"
            )

        self.__net_name = stm[1]
        filename = stm[3]

        if os.path.isfile(filename):
            return "%s = nx.read_edgelist('%s')\n" % (self.__net_name, filename)
        else:
            raise ValueError(
                "Experiment description malformed (file not existing): check your syntax"
            )

    def __model_creation(self, desc):

        if len(desc) > 1:
            raise ValueError("Unsupported description")
        self.__model_name = desc[0].split(" ")[1]
        create = "%s = CompositeModel(%s)\n" % (self.__model_name, self.__net_name)
        return create

    def __model_configuration(self, desc):

        components = {"INITIALIZE": None, "SET": []}

        for part in desc:
            part = part.split(" ")
            if part[0] not in components:
                raise ValueError("Unsupported description")
            if part[0] == "SET":
                if len(part[0]) < 3:
                    raise ValueError(
                        "Experiment description malformed: check your syntax"
                    )
                else:
                    components["SET"].append((part[1], part[2]))
        conf = "config = Configuration()\n"
        for cf in components["SET"]:
            status = cf[0].lower()
            if status not in self.__statuses:
                raise ValueError("Configuration Error: status not defined")

            conf += "config.add_model_parameter('percentage_%s', %s)\n" % (
                status,
                cf[1],
            )
        conf += "%s.set_initial_status(config)\n" % self.__model_name
        return conf

    def __rule_definition(self, desc):

        components = {"RULE": None, "FROM": None, "TO": None, "USING": None}
        for part in desc:
            part = part.split(" ")
            if part[0] not in components:
                raise ValueError("Unsupported description")
            if part[0] != "RULE":
                if len(part) == 2:
                    components[part[0]] = part[1]
                else:
                    raise ValueError("Unsupported parameter")

        if (
            components["FROM"].lower() not in self.__statuses
            or components["TO"].lower() not in self.__statuses
        ):
            raise ValueError("Rule Definition Error: status not defined")

        if components["USING"] not in self.__compartments:
            raise ValueError(
                "Conditional Compartment Definition Error: compartment '%s' undefined"
                % components["USING"]
            )

        apply = "%s.add_rule('%s', '%s', %s)\n" % (
            self.__model_name,
            components["FROM"],
            components["TO"],
            components["USING"],
        )
        return apply

    def __compartment_definition(self, desc):

        components = {
            "COMPARTMENT": None,
            "TYPE": None,
            "TRIGGER": None,
            "COMPOSE": None,
            "PARAM": {
                "probability": 1,
                "threshold": None,
                "rate": None,
                "attribute": None,
                "attribute_value": None,
                "name": None,
                "iterations": None,
            },
        }
        for part in desc:
            part = part.split(" ")
            if part[0] not in components:
                raise ValueError("Unsupported description")
            if len(part) == 2:
                components[part[0]] = part[1]
            else:
                if part[1] not in components["PARAM"]:
                    raise ValueError("Unsupported parameter")
                components["PARAM"][part[1]] = part[2]

        if (
            components["TRIGGER"] is not None
            and components["TRIGGER"].lower() not in self.__statuses
        ):
            raise ValueError("Rule Definition Error: status not defined")

        self.__compartments[components["COMPARTMENT"]] = components["TYPE"]

        rule = (
            "%s = %s(composed=%s, triggering_status='%s', "
            "rate=%s, probability=%s, threshold=%s, attribute='%s', attribute_value=%s, name=\"%s\", iterations=%s)\n"
            % (
                components["COMPARTMENT"],
                components["TYPE"],
                components["COMPOSE"],
                components["TRIGGER"],
                components["PARAM"]["rate"],
                components["PARAM"]["probability"],
                components["PARAM"]["threshold"],
                components["PARAM"]["attribute"],
                components["PARAM"]["attribute_value"],
                components["PARAM"]["name"],
                components["PARAM"]["iterations"],
            )
        )

        rule = rule.replace("'None'", "None")

        # Code cleaning
        rule = re.sub(", [a-zA-Z\\_]+=None", "", rule)
        rule = rule.replace("  ", " ")
        rule = re.sub("[a-zA-Z\\_]+=None,", "", rule)
        rule = rule.replace("( ", "(")

        return rule

    def __conditional_compartment_composition(self, desc):

        components = ["IF", "THEN", "ELSE", "AS"]

        for part in desc:
            part = part.split(" ")
            if (
                part[0] not in components
                or part[2] not in components
                or part[4] not in components
                or part[6] not in components
            ):
                raise ValueError("Unsupported description")
            if len(part) == 8:

                if (
                    part[1] not in self.__compartments
                    or part[3] not in self.__compartments
                    or part[5] not in self.__compartments
                ):
                    raise ValueError(
                        "Conditional Compartment Definition Error: compartment undefined"
                    )

                self.__compartments[part[-1]] = "ConditionalComposition"
                return "%s = ConditionalComposition(%s, %s, %s)\n" % (
                    part[-1],
                    part[1],
                    part[3],
                    part[5],
                )
            else:
                raise ValueError("Experiment description malformed: check your syntax")

    @staticmethod
    def __check_components(identified_directives):

        # Check model
        if "MODEL" not in identified_directives:
            raise ValueError(
                "Experiment description malformed (Model not specified): check your syntax"
            )

        # Check network
        if "LOAD_NETWORK" not in identified_directives:
            if "CREATE_NETWORK" not in identified_directives:
                raise ValueError(
                    "Experiment description malformed (Network not specified): check your syntax"
                )
        else:
            if "CREATE_NETWORK" in identified_directives:
                ValueError(
                    "Experiment description malformed (Network not specified): check your syntax"
                )

        # Check execution
        if "EXECUTE" not in identified_directives:
            raise ValueError(
                "Experiment description malformed (Execution statement missing): check your syntax"
            )

        # Initial status
        if "INITIALIZE" not in identified_directives:
            raise ValueError(
                "Experiment description malformed (Initial status missing): check your syntax"
            )

    @staticmethod
    def __sanitize_string(text):
        text = (
            text.replace("\t", " ")
            .replace("eval", "")
            .replace("exec", "")
            .replace("__", "")
        )
        return re.sub("[-\\\():=!@#$]", "", text)
