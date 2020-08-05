# TODO Dynamic graph, plots, attribute updating, multiple status implementation (?), optimize speed

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

def intial_status(node, graph):
    addiction = 0
    return addiction

def craving_model(node, graph, current_val, variable):
    craving = nx.get_node_attributes(graph, 'craving')[node]
    self_control = nx.get_node_attributes(graph, 'self_control')[node]
    return min(current_val + craving - self_control, 1)

# Network definition
g = nx.erdos_renyi_graph(n=100, p=0.1)

# Extra network setup
attr = {n: {'craving': random.random(), 'self_control': random.random()} for n in g.nodes()}
nx.set_node_attributes(g, attr)

print('initial nodes:')
for n in g.nodes(data=True):
    print(n)
print()

# Model definition
addiction_model = ContinuousModel(g)
addiction_model.add_status('addiction')

# Compartments
condition = NodeNumericalAttribute('self_control', value='craving', op='<')

# Rules
addiction_model.add_rule('addiction', craving_model, condition)

# Configuration
config = mc.Configuration()
config.add_model_parameter('fraction_infected', 0.1)
addiction_model.set_initial_status(intial_status, config)

# Simulation
iterations = addiction_model.iteration_bunch(200, node_status=True)

print()
print(iterations)
print()

### Plots / data manipulation
# Mean status delta per iterations
means = []
for it in iterations:
    deltas = list(it['status_delta'].values())
    if len(deltas) > 0:
        means.append(sum(deltas) / len(deltas))
    else:
        means.append(0)

x = np.arange(0, len(iterations))

plt.plot(x, means)
plt.show()