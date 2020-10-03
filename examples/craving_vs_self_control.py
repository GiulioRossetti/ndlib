import sys
sys.path.append("..")

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

from ndlib.models.ContinuousModel import ContinuousModel
from ndlib.models.compartments.NodeStochastic import NodeStochastic

import ndlib.models.ModelConfig as mc

################### MODEL SPECIFICATIONS ###################

constants = {
    'q': 0.8,
    'b': 0.5,
    'd': 0.2,
    'h': 0.2,
    'k': 0.25,
    'S+': 0.5,
}
constants['p'] = 2*constants['d']

def initial_v(node, graph, status, constants):
    return min(1, max(0, status['C']-status['S']-status['E']))

def initial_a(node, graph, status, constants):
    return constants['q'] * status['V'] + (np.random.poisson(status['lambda'])/7)

initial_status = {
    'C': 0,
    'S': constants['S+'],
    'E': 1,
    'V': initial_v,
    'lambda': 0.5,
    'A': initial_a
}

def update_C(node, graph, status, attributes, constants):
    return status[node]['C'] + constants['b'] * status[node]['A'] * min(1, 1-status[node]['C']) - constants['d'] * status[node]['C']

def update_S(node, graph, status, attributes, constants):
    return status[node]['S'] + constants['p'] * max(0, constants['S+'] - status[node]['S']) - constants['h'] * status[node]['C'] - constants['k'] * status[node]['A']

def update_E(node, graph, status, attributes, constants):
    # return status[node]['E'] - 0.015 # Grasman calculation

    avg_neighbor_addiction = 0
    for n in graph.neighbors(node):
        avg_neighbor_addiction += status[n]['A']

    return max(-1.5, status[node]['E'] - avg_neighbor_addiction / 50) # Custom calculation

def update_V(node, graph, status, attributes, constants):
    return min(1, max(0, status[node]['C']-status[node]['S']-status[node]['E']))

def update_lambda(node, graph, status, attributes, constants):
    return status[node]['lambda'] + 0.01

def update_A(node, graph, status, attributes, constants):
    return constants['q'] * status[node]['V'] + min((np.random.poisson(status[node]['lambda'])/7), constants['q']*(1 - status[node]['V']))

################### MODEL CONFIGURATION ###################

# Network definition
# g = nx.random_geometric_graph(2000, 0.035)
g = nx.random_geometric_graph(200, 0.125)

# Visualization config
visualization_config = {
    'plot_interval': 2,
    'plot_variable': 'A',
    'variable_limits': {
        'A': [0, 0.8],
        'lambda': [0.5, 1.5]
    },
    'show_plot': False,
    'plot_output': '../../animations/c_vs_s.gif',
    'plot_title': 'Self control vs craving simulation',
}

# Model definition
craving_control_model = ContinuousModel(g, constants=constants)
craving_control_model.add_status('C')
craving_control_model.add_status('S')
craving_control_model.add_status('E')
craving_control_model.add_status('V')
craving_control_model.add_status('lambda')
craving_control_model.add_status('A')

# Compartments
condition = NodeStochastic(1)

# Rules
craving_control_model.add_rule('C', update_C, condition)
craving_control_model.add_rule('S', update_S, condition)
craving_control_model.add_rule('E', update_E, condition)
craving_control_model.add_rule('V', update_V, condition)
craving_control_model.add_rule('lambda', update_lambda, condition)
craving_control_model.add_rule('A', update_A, condition)

# Configuration
config = mc.Configuration()
craving_control_model.set_initial_status(initial_status, config)
craving_control_model.configure_visualization(visualization_config)

################### SIMULATION ###################

# Simulation
iterations = craving_control_model.iteration_bunch(100, node_status=True)
trends = craving_control_model.build_trends(iterations)

################### VISUALIZATION ###################

craving_control_model.plot(trends, len(iterations), delta=True)

x = np.arange(0, len(iterations))
plt.figure()

plt.subplot(221)
plt.plot(x, trends['means']['E'], label='E')
plt.plot(x, trends['means']['lambda'], label='lambda')
plt.legend()

plt.subplot(222)
plt.plot(x, trends['means']['A'], label='A')
plt.plot(x, trends['means']['C'], label='C')
plt.legend()

plt.subplot(223)
plt.plot(x, trends['means']['S'], label='S')
plt.plot(x, trends['means']['V'], label='V')
plt.legend()

plt.show()

craving_control_model.visualize(iterations)
