__author__ = 'Giulio Rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"


class Configuration(object):

    def __init__(self):
        self.config = {
            'nodes': {},
            'edges': {},
            'model': {},
            'status': {}
        }

    def get_nodes_configuration(self):
        return self.config['nodes']

    def get_edges_configuration(self):
        return self.config['edges']

    def get_model_parameters(self):
        return self.config['model']

    def get_model_configuration(self):
        return self.config['status']

    def add_model_parameter(self, param_name, param_value):
        self.config['model'][param_name] = param_value

    def add_model_initial_configuration(self, status_name, nodes):
        self.config['status'][status_name] = nodes

    def add_node_configuration(self, param_name, node_id, param_value):
        if param_name not in self.config['nodes']:
            self.config['nodes'][param_name] = {node_id: param_value}
        else:
            self.config['nodes'][param_name][node_id] = param_value

    def add_node_set_configuration(self, param_name, node_to_value):
        for nid, val in node_to_value.iteritems():
            self.add_node_configuration(param_name, nid, val)

    def add_edge_configuration(self, param_name, edge, param_value):
        if param_name not in self.config['edges']:
            self.config['edges'][param_name] = {edge: param_value}
        else:
            self.config['edges'][param_name][edge] = param_value

    def add_edge_set_configuration(self, param_name, edge_to_value):
        for edge, val in edge_to_value.iteritems():
            self.add_node_configuration(param_name, edge, val)
