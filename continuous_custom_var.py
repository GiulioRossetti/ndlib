# TODO Dynamic graph, more plots, attribute updating, multiple status implementation (?), optimize speed, plotly/gephy visualization of graph

import networkx as nx
import random
import matplotlib.pyplot as plt
import numpy as np

from ndlib.models.CompositeModel import CompositeModel
from ndlib.models.ContinuousModel import ContinuousModel
from ndlib.models.compartments.NodeStochastic import NodeStochastic
from ndlib.models.compartments.NodeNumericalAttribute import NodeNumericalAttribute

import ndlib.models.ModelConfig as mc

from bokeh.io import show
from ndlib.viz.bokeh.DiffusionTrend import DiffusionTrend

def initial_addiction(node, graph):
    addiction = 0
    return addiction

def initial_self_confidence(node, graph):
    self_confidence = 1
    return self_confidence

initial_status = {
    'addiction': initial_addiction,
    'self_confidence': initial_self_confidence
}

def craving_model(node, graph, status, attributes):
    current_val = status[node]['addiction']
    craving = attributes[node]['craving']
    self_control = attributes[node]['self_control']
    return min(current_val + craving - self_control, 1)

def self_confidence_impact(node, graph, status, attributes):
    return max(status[node]['self_confidence'] - random.uniform(0, 0.2), 0)

# Network definition
g = nx.erdos_renyi_graph(n=10000, p=0.1)

# Extra network setup
attr = {n: {'craving': random.random(), 'self_control': random.random()} for n in g.nodes()}
nx.set_node_attributes(g, attr)

# Model definition
addiction_model = ContinuousModel(g)
addiction_model.add_status('addiction')
addiction_model.add_status('self_confidence')

# Compartments
condition = NodeNumericalAttribute('self_control', 'craving', op='<')
condition2 = NodeStochastic(0.5)

# Rules
addiction_model.add_rule('addiction', craving_model, condition)
addiction_model.add_rule('self_confidence', self_confidence_impact, condition2)

# Configuration
config = mc.Configuration()
config.add_model_parameter('fraction_infected', 0.1)
addiction_model.set_initial_status(initial_status, config)

# Simulation
iterations = addiction_model.iteration_bunch(200, node_status=True)

print()
print(iterations)
print()

### Plots / data manipulation

# Mean status delta per iterations
# means = []
# for it in iterations:
#     deltas = list(it['status_delta'].values())
#     if len(deltas) > 0:
#         means.append(sum(deltas) / len(deltas))
#     else:
#         means.append(0)

# x = np.arange(0, len(iterations))

# plt.plot(x, means)
# plt.show()