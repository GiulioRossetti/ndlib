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

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class ExperimentParser(object):

    def __init__(self):
        self.imports = 'import networkx as nx\n' \
                       'import numpy as np\n' \
                       'import json\n' \
                       'from ndlib.models.ModelConfig import Configuration\n' \
                       'from ndlib.models.CompositeModel import CompositeModel\n' \
                       'from ndlib.models.compartments.NodeStochastic import NodeStochastic\n' \
                       'from ndlib.models.compartments.NodeThreshold import NodeThreshold\n' \
                       'from ndlib.models.compartments.NodeCategoricalAttribute import NodeCategoricalAttribute\n' \
                       'from ndlib.models.compartments.NodeNumericalAttribute import NodeNumericalAttribute\n' \
                       'from ndlib.models.compartments.EdgeStochastic import EdgeStochastic\n' \
                       'from ndlib.models.compartments.EdgeCategoricalAttribute import EdgeCategoricalAttribute\n' \
                       'from ndlib.models.compartments.EdgeNumericalAttribute import EdgeNumericalAttribute\n' \
                       'from ndlib.models.compartments.ConditionalComposition import ConditionalComposition\n' \
                       'from ndlib.models.compartments.CountDown import CountDown\n'

        self.script = ""
        self.starting = ('STATUS', 'MODEL', 'COMPARTMENT', 'RULE', 'IF', 'INITIALIZE',
                         'CREATE_NETWORK', 'LOAD_NETWORK', 'EXECUTE')
        self.__model_name = None
        self.__net_name = None
        self.query = None
        self.__statuses = {}
        self.__compartments = {}
        self.model = CompositeModel(nx.Graph())

    def read_query_file(self, filename):
        with open(filename) as f:
            self.query = f.read()

    def set_query(self, query):
        self.query = query

    def parse(self):

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
                raise ValueError("The keyword '%s' is not defined: check your syntax" % key)
            self.script = "%s%s" % (self.script, code)

        self.__clean_imports()
        self.script = "%s\n%s" % (self.imports, self.script)

    def execute_query(self):
        # Query execution
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()

        try:
            exec(self.script, locals(), globals())
        except SyntaxError:
            raise ValueError("Experiment description malformed (Incorrect statement ordering): check your syntax")

        sys.stdout = old_stdout
        result = json.loads(redirected_output.getvalue())
        trends = self.model.build_trends(result)
        trends[0]['Statuses'] = {str(v): k for k, v in self.model.available_statuses.items()}
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
            raise ValueError("Experiment description malformed (wrong status definition statement): check your syntax")
        part = desc[0].split(" ")
        if part[0] != 'STATUS':
            raise ValueError("Experiment description malformed (wrong status definition statement): check your syntax")

        self.__statuses[part[1].lower()] = None
        self.model.add_status(part[1])

        return "%s.add_status('%s')\n" % (self.__model_name, part[1])

    def __execution_statement(self, desc):

        if len(desc) > 1:
            raise ValueError("Experiment description malformed (wrong execution statement): check your syntax")
        part = desc[0].split(" ")
        if part[0] != 'EXECUTE' or part[2] != 'ON' or part[4] != 'FOR':
            raise ValueError("Experiment description malformed (wrong execution statement): check your syntax")

        if self.__model_name != part[1]:
            raise ValueError("Execution Definition Error: model '%s' not defined" % part[1])

        if self.__net_name != part[3]:
            raise ValueError("Execution Definition Error: graph '%s' not defined" % part[3])

        return "iterations = %s.iteration_bunch(%s, node_status=False)\n" \
               "res = json.dumps(iterations)\n" \
               "print(res)\n" % (self.__model_name, part[5])

    def __network_generation(self, desc):

        components = {'CREATE_NETWORK': None, 'TYPE': None, 'PARAM': []}

        for part in desc:
            part = part.split(" ")
            if part[0] not in components:
                raise ValueError("Unsupported description")
            if part[0] == 'PARAM':
                if len(part[0]) < 3:
                    raise ValueError("Experiment description malformed (wrong network definition): check your syntax")
                else:
                    components['PARAM'].append((part[1], part[2]))
            else:
                components[part[0]] = part[1]
        self.__net_name = components['CREATE_NETWORK']
        parameters = ""
        for pr in components['PARAM']:
            parameters += "%s=%s, " % (pr[0], pr[1])
        code = "%s = nx.%s(%s)\n" % (self.__net_name, components['TYPE'], parameters)

        return code.replace(", )", ")")

    def __network_loading(self, desc):

        compartments = ['LOAD_NETWORK', 'FROM']

        if len(desc) > 1:
            raise ValueError("Unsupported description")
        stm = desc[0].split(" ")
        if len(stm) != 4 or stm[0] not in compartments or stm[2] not in compartments:
            raise ValueError("Experiment description malformed (wrong network loading statement): check your syntax")

        self.__net_name = stm[1]
        filename = stm[3]

        if os.path.isfile(filename):
            return "%s = nx.read_edgelist('%s')\n" % (self.__net_name, filename)
        else:
            raise ValueError("Experiment description malformed (file not existing): check your syntax")

    def __model_creation(self, desc):

        if len(desc) > 1:
            raise ValueError("Unsupported description")
        self.__model_name = desc[0].split(" ")[1]
        create = "%s = CompositeModel(%s)\n" % (self.__model_name, self.__net_name)
        return create

    def __model_configuration(self, desc):

        components = {'INITIALIZE': None, 'SET': []}

        for part in desc:
            part = part.split(" ")
            if part[0] not in components:
                raise ValueError("Unsupported description")
            if part[0] == 'SET':
                if len(part[0]) < 3:
                    raise ValueError("Experiment description malformed: check your syntax")
                else:
                    components['SET'].append((part[1], part[2]))
        conf = "config = Configuration()\n"
        for cf in components['SET']:
            status = cf[0].lower()
            if status not in self.__statuses:
                raise ValueError("Configuration Error: status not defined")

            conf += "config.add_model_parameter('percentage_%s', %s)\n" % (status, cf[1])
        conf += "%s.set_initial_status(config)\n" % self.__model_name
        return conf

    def __rule_definition(self, desc):

        components = {'RULE': None, 'FROM': None, 'TO': None, 'USING': None}
        for part in desc:
            part = part.split(" ")
            if part[0] not in components:
                raise ValueError("Unsupported description")
            if part[0] != 'RULE':
                if len(part) == 2:
                    components[part[0]] = part[1]
                else:
                    raise ValueError("Unsupported parameter")

        if components['FROM'].lower() not in self.__statuses or components['TO'].lower() not in self.__statuses:
            raise ValueError("Rule Definition Error: status not defined")

        if components['USING'] not in self.__compartments:
            raise ValueError("Conditional Compartment Definition Error: compartment '%s' undefined"
                             % components['USING'])

        apply = "%s.add_rule('%s', '%s', %s)\n" % (self.__model_name, components['FROM'],
                                                   components['TO'], components['USING'])
        return apply

    def __compartment_definition(self, desc):

        components = {'COMPARTMENT': None, 'TYPE': None, 'TRIGGER': None, 'COMPOSE': None,
                      'PARAM': {'probability': 1, 'threshold': None, 'rate': None, 'attribute': None,
                                'attribute_value': None, 'name': None, 'iterations': None}}
        for part in desc:
            part = part.split(" ")
            if part[0] not in components:
                raise ValueError("Unsupported description")
            if len(part) == 2:
                components[part[0]] = part[1]
            else:
                if part[1] not in components['PARAM']:
                    raise ValueError("Unsupported parameter")
                components['PARAM'][part[1]] = part[2]

        if components['TRIGGER'] is not None and components['TRIGGER'].lower() not in self.__statuses:
            raise ValueError("Rule Definition Error: status not defined")

        self.__compartments[components['COMPARTMENT']] = components['TYPE']

        rule = '%s = %s(composed=%s, triggering_status=\'%s\', ' \
               'rate=%s, probability=%s, threshold=%s, attribute=\'%s\', attribute_value=%s, name="%s", iterations=%s)\n' % \
               (components['COMPARTMENT'], components['TYPE'],
                components['COMPOSE'], components['TRIGGER'],
                components['PARAM']['rate'], components['PARAM']['probability'], components['PARAM']['threshold'],
                components['PARAM']['attribute'], components['PARAM']['attribute_value'], components['PARAM']['name'],
                components['PARAM']['iterations'])

        rule = rule.replace("'None'", "None")

        # Code cleaning
        rule = re.sub(', [a-zA-Z\\_]+=None', '', rule)
        rule = rule.replace("  ", " ")
        rule = re.sub('[a-zA-Z\\_]+=None,', '', rule)
        rule = rule.replace("( ", "(")

        return rule

    def __conditional_compartment_composition(self, desc):

        components = ['IF', 'THEN', 'ELSE', 'AS']

        for part in desc:
            part = part.split(" ")
            if part[0] not in components or part[2] not in components \
                    or part[4] not in components or part[6] not in components:
                raise ValueError("Unsupported description")
            if len(part) == 8:

                if part[1] not in self.__compartments or part[3] not in self.__compartments\
                        or part[5] not in self.__compartments:
                    raise ValueError("Conditional Compartment Definition Error: compartment undefined")

                self.__compartments[part[-1]] = "ConditionalComposition"
                return "%s = ConditionalComposition(%s, %s, %s)\n" \
                       % (part[-1], part[1], part[3], part[5])
            else:
                raise ValueError("Experiment description malformed: check your syntax")

    @staticmethod
    def __check_components(identified_directives):

        # Check model
        if 'MODEL' not in identified_directives:
            raise ValueError("Experiment description malformed (Model not specified): check your syntax")

        # Check network
        if 'LOAD_NETWORK' not in identified_directives:
            if 'CREATE_NETWORK' not in identified_directives:
                raise ValueError("Experiment description malformed (Network not specified): check your syntax")
        else:
            if 'CREATE_NETWORK' in identified_directives:
                ValueError("Experiment description malformed (Network not specified): check your syntax")

        # Check execution
        if 'EXECUTE' not in identified_directives:
            raise ValueError("Experiment description malformed (Execution statement missing): check your syntax")

        # Initial status
        if 'INITIALIZE' not in identified_directives:
            raise ValueError("Experiment description malformed (Initial status missing): check your syntax")

    @staticmethod
    def __sanitize_string(text):
        text = text.replace("\t", " ").replace("eval", "").replace("exec", "").replace("__", "")
        return re.sub('[-\\\():=!@#$]', '', text)
