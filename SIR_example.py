import networkx as nx

from ndlib.models.CompositeModel import CompositeModel
from ndlib.models.compartments.NodeStochastic import NodeStochastic
import ndlib.models.ModelConfig as mc

from bokeh.io import show
from ndlib.viz.bokeh.DiffusionTrend import DiffusionTrend

# Network definition
g1 = nx.erdos_renyi_graph(n=1000, p=0.1)

# Model definition
SIR = CompositeModel(g1)
SIR.add_status('Susceptible')
SIR.add_status('Infected')
SIR.add_status('Removed')

# Compartments
c1 = NodeStochastic(rate=0.02, triggering_status='Infected')
c2 = NodeStochastic(rate=0.01)

# Rules
SIR.add_rule('Susceptible', 'Infected', c1)
SIR.add_rule('Infected', 'Removed', c2)

# Configuration
config = mc.Configuration()
config.add_model_parameter('percentage_infected', 0.1)
SIR.set_initial_status(config)

# Simulation
iterations = SIR.iteration_bunch(300, node_status=False)
trends = SIR.build_trends(iterations)

# Visualization
viz = DiffusionTrend(SIR, trends)
p = viz.plot(width=400, height=400)
show(p)

print(SIR.available_statuses)