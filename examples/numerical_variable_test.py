import sys
sys.path.append("..")

import networkx as nx
import random
import numpy as np

from ndlib.models.CompositeModel import CompositeModel
from ndlib.models.compartments.NodeStochastic import NodeStochastic
from ndlib.models.compartments.enums.NumericalType import NumericalType
from ndlib.models.compartments.NodeNumericalVariable import NodeNumericalVariable
import ndlib.models.ModelConfig as mc

# Network generation
g = nx.erdos_renyi_graph(1000, 0.1)

# Setting edge attribute
attr = {n: {"Age": random.choice(range(0, 100)), "Friends": random.choice(range(0, 100))} for n in g.nodes()}
nx.set_node_attributes(g, attr)

# Composite Model instantiation
model = CompositeModel(g)

# Model statuses
model.add_status("Susceptible")
model.add_status("Infected")
model.add_status("Removed")

# Compartment definition
condition = NodeNumericalVariable('Age', var_type=NumericalType.ATTRIBUTE, value='Friends', value_type=NumericalType.ATTRIBUTE, op='<')
condition2 = NodeNumericalVariable('Friends', var_type=NumericalType.ATTRIBUTE, value=18, op='>')

# Rule definition
model.add_rule("Susceptible", "Infected", condition)
model.add_rule("Infected", "Removed", condition2)

# Model initial status configuration
config = mc.Configuration()
config.add_model_parameter('fraction_infected', 0.5)

# Simulation execution
model.set_initial_status(config)
iterations = model.iteration_bunch(100)
