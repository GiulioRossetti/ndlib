## NDlib - Network Diffusion Library

NDlib provide implementations of several spreading and opinion dynamics models.
It is implemented in Python 2.7 (support for Python 3.x pending).

### Installation

In order to install the library just download (or clone) the current project and copy the ndlib folder in the root of your application (installation via pip will be supported in the near future).

### Rationale behind the implemented models

NDlib describe diffusion models as agent-based simulations occurring at discrete time: once configured the desired model and selected the target network, subsequent iterations will provide to the user the current status of each node.

### Example usage

Import the selected diffusion model with
```python
import ndlib.VoterModel as vm
```

Generate/load a graph with the [networkx](https://networkx.github.io/) library
```python
import networkx as nx
g = nx.erdos_renyi_graph(1000, 0.1)
```

Initialize the model on the graph
```
model = vm.VoterModel(g)
```

Set the nodel initial status
```
model.set_initial_status({'model': {'percentage_infected': 0.2}})
```

Request a single iteration of the simulation
```
it_id, it_status = model.iteration()
```
or a bunch of iterations
```
it_bunch = model.iteration_bunch(bunch_size=10)
``` 
