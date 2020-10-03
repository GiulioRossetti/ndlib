import sys
sys.path.append("..")

import networkx as nx
import random
import numpy as np

from ndlib.models.ContinuousModel import ContinuousModel
from ndlib.models.compartments.enums.NumericalType import NumericalType
from ndlib.models.compartments.NodeNumericalVariable import NodeNumericalVariable

import ndlib.models.ModelConfig as mc

from bokeh.io import show
from ndlib.viz.bokeh.DiffusionTrend import DiffusionTrend

def initial_addiction(node, graph, status, constants):
    addiction = 0
    return addiction

def initial_self_confidence(node, graph, status, constants):
    self_confidence = 1
    return self_confidence

initial_status = {
    'addiction': initial_addiction,
    'self_confidence': initial_self_confidence
}

def craving_model(node, graph, status, attributes, constants):
    current_val = status[node]['addiction']
    craving = attributes[node]['craving']
    self_control = attributes[node]['self_control']
    return min(current_val + craving - self_control, 1)

def self_confidence_impact(node, graph, status, attributes, constants):
    return max(status[node]['self_confidence'] - random.uniform(0.2, 0.5), 0)

# Network definition
g = nx.erdos_renyi_graph(n=1000, p=0.1)

# Extra network setup
attr = {n: {'craving': random.random(), 'self_control': random.random()} for n in g.nodes()}
nx.set_node_attributes(g, attr)

# Visualization config
visualization_config = {
    'plot_interval': 10,
    'plot_variable': 'addiction',
    'show_plot': True,
    'plot_title': 'Example model',
    'animation_interval': 500
}

# Model definition
addiction_model = ContinuousModel(g)
addiction_model.add_status('addiction')
addiction_model.add_status('self_confidence')

# Compartments
condition = NodeNumericalVariable('self_control', var_type=NumericalType.ATTRIBUTE, value='craving', value_type=NumericalType.ATTRIBUTE, op='<')
condition2 = NodeNumericalVariable('addiction', var_type=NumericalType.STATUS, value=1, op='==')

# Rules
addiction_model.add_rule('addiction', craving_model, condition)
addiction_model.add_rule('self_confidence', self_confidence_impact, condition2)

# Configuration
config = mc.Configuration()
addiction_model.set_initial_status(initial_status, config)
addiction_model.configure_visualization(visualization_config)

# Simulation
iterations = addiction_model.iteration_bunch(200, node_status=True)

trends = addiction_model.build_trends(iterations)
addiction_model.plot(trends, len(iterations), delta=True)

### Plots / data manipulation
addiction_model.visualize(iterations)
