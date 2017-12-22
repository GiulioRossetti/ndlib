import future.utils

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class Configuration(object):
    """
    Configuration Object

    """

    def __init__(self):
        self.config = {
            'nodes': {},
            'edges': {},
            'model': {},
            'status': {}
        }

    def get_nodes_configuration(self):
        """
        Nodes configurations

        :return: dictionary that link each node to its attributes
        """
        return self.config['nodes']

    def get_edges_configuration(self):
        """
        Edges configurations

        :return: dictionary that link each edge to its attributes
        """
        return self.config['edges']

    def get_model_parameters(self):
        """
        Model parameters

        :return: dictionary describes the specified model parameters
        """
        return self.config['model']

    def get_model_configuration(self):
        """
        Initial configuration

        :return: initial nodes status (if specified)
        """
        return self.config['status']

    def add_model_parameter(self, param_name, param_value):
        """
        Set a Model Parameter

        :param param_name: parameter identifier (as specified by the chosen model)
        :param param_value: parameter value
        """
        self.config['model'][param_name] = param_value

    def add_model_initial_configuration(self, status_name, nodes):
        """
        Set initial status for a set of nodes

        :param status_name: status to be set (as specified by the chosen model)
        :param nodes: list of affected nodes
        """
        self.config['status'][status_name] = nodes

    def add_node_configuration(self, param_name, node_id, param_value):
        """
        Set a parameter for a given node

        :param param_name: parameter identifier (as specified by the chosen model)
        :param node_id: node identifier
        :param param_value: parameter value
        """
        if param_name not in self.config['nodes']:
            self.config['nodes'][param_name] = {node_id: param_value}
        else:
            self.config['nodes'][param_name][node_id] = param_value

    def add_node_set_configuration(self, param_name, node_to_value):
        """
        Set Nodes parameter

        :param param_name: parameter identifier (as specified by the chosen model)
        :param node_to_value: dictionary mapping each node a parameter value
        """
        for nid, val in future.utils.iteritems(node_to_value):
            self.add_node_configuration(param_name, nid, val)

    def add_edge_configuration(self, param_name, edge, param_value):
        """
        Set a parameter for a given edge

        :param param_name: parameter identifier (as specified by the chosen model)
        :param edge: edge identifier
        :param param_value: parameter value
        """
        if param_name not in self.config['edges']:
            self.config['edges'][param_name] = {edge: param_value}
        else:
            self.config['edges'][param_name][edge] = param_value

    def add_edge_set_configuration(self, param_name, edge_to_value):
        """
        Set Edges parameter

        :param param_name: parameter identifier (as specified by the chosen model)
        :param edge_to_value: dictionary mapping each edge a parameter value
        """
        for edge, val in future.utils.iteritems(edge_to_value):
            self.add_edge_configuration(param_name, edge, val)
