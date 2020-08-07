# TODO Dynamic graph, more plots, optimize speed (?), plotly/gephy visualization of graph

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
    return constants['q'] * status['V'] + (np.random.poisson(status['labda'])/7)

initial_status = {
    'C': 0,
    'S': constants['S+'],
    'E': 1,
    'V': initial_v,
    'labda': 0.5,
    'A': initial_a
}

def update_C(node, graph, status, attributes, constants):
    return status[node]['C'] + constants['b'] * status[node]['A'] * min(1, 1-status[node]['C']) - constants['d'] * status[node]['C']

def update_S(node, graph, status, attributes, constants):
    return status[node]['S'] + constants['p'] * max(0, constants['S+'] - status[node]['S']) - constants['h'] * status[node]['C'] - constants['k'] * status[node]['A']

def update_E(node, graph, status, attributes, constants):
    return status[node]['E'] - 0.015

def update_V(node, graph, status, attributes, constants):
    return min(1, max(0, status[node]['C']-status[node]['S']-status[node]['E']))

def update_labda(node, graph, status, attributes, constants):
    return status[node]['labda'] + 0.01

def update_A(node, graph, status, attributes, constants):
    return constants['q'] * status[node]['V'] + min((np.random.poisson(status[node]['labda'])/7), constants['q']*(1 - status[node]['V']))

# Network definition
g = nx.erdos_renyi_graph(n=1, p=0.1)

# Model definition
craving_control_model = ContinuousModel(g, constants=constants)
craving_control_model.add_status('C')
craving_control_model.add_status('S')
craving_control_model.add_status('E')
craving_control_model.add_status('V')
craving_control_model.add_status('labda')
craving_control_model.add_status('A')

# Compartments
condition = NodeStochastic(1)

# Rules
craving_control_model.add_rule('C', update_C, condition)
craving_control_model.add_rule('S', update_S, condition)
craving_control_model.add_rule('E', update_E, condition)
craving_control_model.add_rule('V', update_V, condition)
craving_control_model.add_rule('labda', update_labda, condition)
craving_control_model.add_rule('A', update_A, condition)

# Configuration
config = mc.Configuration()
config.add_model_parameter('fraction_infected', 0.1)
craving_control_model.set_initial_status(initial_status, config)

# Simulation
iterations = craving_control_model.iteration_bunch(100, node_status=True)
trends = craving_control_model.build_trends(iterations)

### Plots / data manipulation

# craving_control_model.visualize(trends, len(iterations), delta=True)


x = np.arange(0, len(iterations))
plt.figure()

plt.subplot(221)
plt.plot(x, trends['means']['E'], label='E')
plt.plot(x, trends['means']['labda'], label='labda')
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