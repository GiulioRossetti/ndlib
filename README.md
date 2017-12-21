# NDlib - Network Diffusion Library

[![Build Status](https://travis-ci.org/GiulioRossetti/ndlib.svg?branch=master)](https://travis-ci.org/GiulioRossetti/ndlib)
[![Coverage Status](https://coveralls.io/repos/github/GiulioRossetti/ndlib/badge.svg?branch=master)](https://coveralls.io/github/GiulioRossetti/ndlib?branch=master)
[![Documentation Status](https://readthedocs.org/projects/ndlib/badge/?version=latest)](http://ndlib.readthedocs.io/en/latest/?badge=latest)
[![pyversions](https://img.shields.io/pypi/pyversions/ndlib.svg)](https://badge.fury.io/py/ndlib)
[![Updates](https://pyup.io/repos/github/GiulioRossetti/ndlib/shield.svg)](https://pyup.io/repos/github/GiulioRossetti/ndlib/)
[![PyPI version](https://badge.fury.io/py/ndlib.svg)](https://badge.fury.io/py/ndlib)

![NDlib logo](https://github.com/GiulioRossetti/ndlib/blob/master/docs/ndlogo2.png)

NDlib provides implementations of several spreading and opinion dynamics models.

The project documentation can be found on [ReadTheDocs](http://ndlib.readthedocs.io).

If you use ``NDlib`` as support to your research consider citing:

> G. Rossetti, L. Milli, S. Rinzivillo, A. Sirbu, D. Pedreschi, F. Giannotti.
> **NDlib: a Python Library to Model and Analyze Diffusion Processes Over Complex Networks.**
> Journal of Data Science and Analytics. 2017. 
> [DOI:0.1007/s41060-017-0086-6](https://doi.org/10.1007/s41060-017-0086-6)

> G. Rossetti, L. Milli, S. Rinzivillo, A. Sirbu, D. Pedreschi, F. Giannotti.
> "**NDlib: Studying Network Diffusion Dynamics**", 
> IEEE International Conference on Data Science and Advanced Analytics, DSAA. 2017.


## Rationale behind NDlib

- A __simulation__ is univocally identified by a __graph__ and a (__configured__) __model__;
- Each __model__ describes a peculiar kind of diffusion process as an agent-based __simulation__ occurring at discrete time;
- A __configuration__ identifies the initial status of the diffusion and the parameters needed to instantiate the selected __model__;
- Once a model has been __configured__, every __iteration__ of the __simulation__ returns only the nodes which changed their statuses.

## Installation

In order to install the library just download (or clone) the current project and copy the ndlib folder in the root of your application.
Alternatively use pip:
```bash
sudo pip install ndlib
```

## Example usage

Generate/load a graph with the [networkx](https://networkx.github.io/) library
```python
import networkx as nx
g = nx.erdos_renyi_graph(1000, 0.1)
```

Import and initialize the selected diffusion model
```python
import ndlib.models.VoterModel as m
model = m.VoterModel(g)
```

Configure model initial status
```python
import ndlib.models.ModelConfig as mc
config = mc.Configuration()
config.add_model_parameter('percentage_infected', 0.2)
model.set_initial_status(config)
```

Execute an iteration of the simulation
```python
it_id, it_status = model.iteration()
```

Execute a bunch of iterations
```python
it_bunch = model.iteration_bunch(bunch_size=10)
``` 

Each model defines its own node statuses: to retrieve the map used by a given model to identify the available use
```python
model.get_status_map()
```

## Model Configuration Object

Model configuration are defined by a ```ndlib.models.ModelConfig``` object that handle four categories of parameters:
- **model** parameters: ```add_model_parameter(name, value)```
- **node** parameters: ```add_node_configuration(param_name, node_id, param_value)```
- **edge** parameters: ```add_edge_configuration(param_name, edge, param_value)```
- simulation initial **status**: ```add_model_initial_configuration(status_name, node_list)```

We identify a parameter of a given categories as ```category:parameter_name```.

The the complete list of parameters needed by a model are retrievable through
```python
model.get_model_parameters()
```

Moreover, if the initial set of *Infected* nodes is not given it is mandatory to specify the percentage of infected through ```add_model_parameter("percentage_infected", p)```. 
Doing so *p%* of randomly chosen nodes will be selected as the diffusion seeds. 


## Visualize simulation Results

NDlib comes with basic visualization facilities embedded in ```ndlib.viz.bokeh.DiffusionTrend``` and ```ndlib.viz.mpl.DiffusionTrend```.

```python
import networkx as nx
from bokeh.io import show
import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics.SIRModel as sir
from ndlib.viz.bokeh.DiffusionTrend import DiffusionTrend

g = nx.erdos_renyi_graph(1000, 0.1)
model = sir.SIRModel(g)
config = mc.Configuration()
config.add_model_parameter('beta', 0.001)
config.add_model_parameter('gamma', 0.01)
config.add_model_parameter("percentage_infected", 0.05)
model.set_initial_status(config)
iterations = model.iteration_bunch(200)
trends = model.build_trends(iterations)
viz = DiffusionTrend(model, trends)
p = viz.plot()
show(p)
```

In order to visually compare multiple executions it is possible to generate multi plots:

```python
import networkx as nx
from bokeh.io import show
import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics.SIRModel as sir
from ndlib.viz.bokeh.DiffusionPrevalence import DiffusionPrevalence
from ndlib.viz.bokeh.DiffusionTrend import DiffusionTrend 
from ndlib.viz.bokeh.MultiPlot import MultiPlot

vm = MultiPlot()

g = nx.erdos_renyi_graph(1000, 0.1)
model = sir.SIRModel(g)
config = mc.Configuration()
config.add_model_parameter('beta', 0.001)
config.add_model_parameter('gamma', 0.01)
config.add_model_parameter("percentage_infected", 0.05)
model.set_initial_status(config)
iterations = model.iteration_bunch(200)
trends = model.build_trends(iterations)

viz = DiffusionTrend(model, trends)
p = viz.plot()
vm.add_plot(p)

viz2 = DiffusionPrevalence(model, trends)
p2 = viz2.plot()
vm.add_plot(p2)

m = vm.plot()
show(m)
```

Matplotlib based visualizations, offered by ```ndlib.viz.bokeh.DiffusionTrend```, also support out-of-the-box model comparisons.

## Implement new models
Implement additional models is simple since it only requires to define a class that:
- implement the partial abstract ```class ndlib.models.DiffusionModel```;
- redefine the ```__init__()``` method to provide model details;
- implement the ```iteration(node_status)``` method specifying its agent-based rules.

### Structure Example
```python
from ndlib.models.DiffusionModel import DiffusionModel

class MyModel(DiffusionModel):

	def __init__(self, graph):
		super(self.__class__, self).__init__(graph)
		self.available_statuses = {
			"Susceptible": 0, 
			"Infected": 1
		}
		self.parameters = {
			"model": {
				"param1": {
					"descr": "descr1",
					"range": [0, 1],
					"optional": False},
				"param2": {
					"descr": "descr2",
					"range": [0, 1],
					"optional": True}
				},
			"nodes": {
				"param3": {
					"descr": "descr3",
					"range": [0, 1],
					"optional": True},
				"param4": {
					"descr": "descr4",
					"range": [0, 1],
					"optional": True}
				},
			"edges": {
				"param5": {
					"descr": "descr5",
					"range": [0, 1],
					"optional": False},
				"param6": {
					"descr": "descr6",
					"range": [0, 1],
					"optional": True}
				},
			}
		self.name = "MyModel"
	
	
	def iteration(self, node_status=True):
	
		self.clean_initial_status(self.available_statuses.values())
		# if first iteration return the initial node status
		if self.actual_iteration == 0:
			self.actual_iteration += 1
			delta, node_count, status_delta = self.status_delta(actual_status)
			if node_status:
				return {"iteration": 0, "status": actual_status.copy(), 
						"node_count": node_count.copy(), "status_delta": status_delta.copy()}
			else:
				return {"iteration": 0, "status": {}, 
						"node_count": node_count.copy(), "status_delta": status_delta.copy()}
		
		actual_status = {node: nstatus for node, nstatus in self.status.iteritems()}
		for u in self.graph.nodes():
			# evluate possible status changes using the model parameters (accessible via self.params)
			# e.g. self.params['beta'], self.param['nodes']['threshold'][u], self.params['edges'][(id_node0, idnode1)]
		
		# identify the changes w.r.t. previous iteration
		delta, node_count, status_delta = self.status_delta(actual_status)
		
		# update the actual status and iterative step
		self.status = actual_status
		self.actual_iteration += 1
		
		# return the actual configuration (only nodes with status updates)
		if node_status:
			return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
					"node_count": node_count.copy(), "status_delta": status_delta.copy()}
		else:
			return {"iteration": self.actual_iteration - 1, "status": {},
			"node_count": node_count.copy(), "status_delta": status_delta.copy()}

```
If you like to include your model in NDlib (as well as in [NDlib-REST](https://github.com/GiulioRossetti/ndlib-rest)) feel free to fork the project, open an issue and contact us.
