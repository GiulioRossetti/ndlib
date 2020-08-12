# TODO Dynamic graph, integrate with ndlib correctly, plot speed optimizations for large node amount (intermediate images? / matplotlib?), write tests
# Requirements, networkx, numpy, matplotlib, bokeh, plotly, PIL, psutil, kaleido

import networkx as nx
import random
import numpy as np
import matplotlib.pyplot as plt

from ndlib.models.CompositeModel import CompositeModel
from ndlib.models.ContinuousModel import ContinuousModel
from ndlib.models.compartments.NodeStochastic import NodeStochastic
from ndlib.models.compartments.enums.NumericalType import NumericalType
from ndlib.models.compartments.NodeNumericalVariable import NodeNumericalVariable

import ndlib.models.ModelConfig as mc

from bokeh.io import show
from ndlib.viz.bokeh.DiffusionTrend import DiffusionTrend

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

# 50% chance of severing connections, move to random location, create new random connections
def update_network(node, graph, status, attributes, constants):
    sever = []
    for n in graph.neighbors(node):
        if random.random() < 0.5:
            sever.append(n)
    graph.remove_edges(node, sever)

    if random.random() < 0.05:
        pos = (random.random(), random.random())
        graph.nodes[node]['pos'] = pos

    while True:
        new_connections = []
        if random.random() < 0.5:
            new_conn = random.choice(graph.nodes())
            if new_conn not in graph.neighbors(node):
                new_connections.append(new_conn)
        else:
            graph.add_edges(node, new_connections)
            return

################### MODEL CONFIGURATION ###################

# Network definition
g = nx.random_geometric_graph(2000, 0.035)
# g = nx.random_geometric_graph(100, 0.125)

# Visualization config
visualization_config = {
    'plot_interval': 5,
    'plot_variable': 'A',
    'save_plot': True,
    'plot_output': './animations/network.gif',
    'plot_title': 'Self control vs craving simulation',
    'plot_annotation': 'The dynamics of addiction: Craving versus self-control, Johan Grasman, Raoul P.P.P. Grasman, Han L.J. van der Maas (2006)'
}

# Model definition
craving_control_model = ContinuousModel(g, constants=constants, visualization_configuration=visualization_config)
craving_control_model.add_status('C')
craving_control_model.add_status('S')
craving_control_model.add_status('E')
craving_control_model.add_status('V')
craving_control_model.add_status('lambda')
craving_control_model.add_status('A')

# Compartments
condition = NodeStochastic(1)
condition2 = NodeStochastic(0.005)

# Rules
craving_control_model.add_rule('C', update_C, condition)
craving_control_model.add_rule('S', update_S, condition)
craving_control_model.add_rule('E', update_E, condition)
craving_control_model.add_rule('V', update_V, condition)
craving_control_model.add_rule('lambda', update_lambda, condition)
craving_control_model.add_rule('A', update_A, condition)
craving_control_model.add_rule('network', update_network, condition2)

# Configuration
config = mc.Configuration()
config.add_model_parameter('fraction_infected', 0.1)
craving_control_model.set_initial_status(initial_status, config)




################### SIMULATION ###################

# Simulation
iterations = craving_control_model.iteration_bunch(100, node_status=True)
trends = craving_control_model.build_trends(iterations)




################### VISUALIZATION ###################

# craving_control_model.plot(trends, len(iterations), delta=True)

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

craving_control_model.visualize()
