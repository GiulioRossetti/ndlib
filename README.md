# NDlib - Network Diffusion Library

NDlib provides implementations of several spreading and opinion dynamics models.
It is implemented in Python 2.7 (support for Python 3.x pending).

At the moment NDlib makes available the following models

**EPIDEMICS**

1. **SI** *(SIModel)*
 - W. O. Kermack and Ag McKendrick. A Contribution to the Mathematical Theory of Epidemics. Proceedings of the Royal Society of London. Series A, Containing Papers of a Mathematical and Physical Character, 1927.
2. **SIR** *(SIRModel)*
 - W. O. Kermack and Ag McKendrick. A Contribution to the Mathematical Theory of Epidemics. Proceedings of the Royal Society of London. Series A, Containing Papers of a Mathematical and Physical Character, 1927.
3. **SIS** *(SISModel)*
 - W. O. Kermack and Ag McKendrick. A Contribution to the Mathematical Theory of Epidemics. Proceedings of the Royal Society of London. Series A, Containing Papers of a Mathematical and Physical Character, 1927.
4. **Threshold** *(ThresholdModel)*
 - M. Granovetter. Threshold models of collective behavior. American Journal of Sociology, 1978  
5. **Kertesz Threshold** *(KerteszThresholdModel)*
 - Karsai M., Iniguez G., Kaski K., and Kertesz J., Complex contagion process in spreading of online innovation. Journal of the Royal Society, 11(101), 2014
6. **Independent Cascades** *(IndependentCascadeModel)*
 - D. Kempe, J. Kleinberg, and E. Tardos. Maximizing the Spread of Influence through a Social Network. In KDD, 2003.
7. **Profile** *(ProfileModel)*
8. **Profile Threshold** *(ProfileThresholdModel)*
 
**OPINION DYNAMICS**

9. **Voter** *(VoterModel)*
 - Peter Clifford and Aidan Sudbury. A model for spatial conflict. Biometrika, 60(3), 1973. 
10. **QVoter** *(QVoterModel)*
 - Claudio Castellano, Miguel A Mu~noz, and Romualdo Pastor-Satorras. Nonlinear q-voter model. Physical Review E, 80(4), 2009.  
11. **Majority Rule** *(MajorityRuleModel)*
 - S Galam. Real space renormalization group and totalitarian paradox of majority rule voting. Physica A, 285, 2000.  
12. **Snajzd** *(SznajdModel)*
 - Katarzyna Sznajd-Weron and Jozef Sznajd. Opinion evolution in closed community. International Journal of Modern Physics C, 11(06), 2000. 
13. **Cognitive Opinion Dynamics** *(CognitiveOpDynModel)*
 - Francesca Giardini, Daniele Vilone, and Rosaria Conte. Consensus emerging from the bottom-up: the role of cognitive variables in opinion dynamics. Frontiers in Physics, 2015  

## Installation

In order to install the library just download (or clone) the current project and copy the ndlib folder in the root of your application (installation via pip will be supported in the near future).

## Example usage

Import the selected diffusion model with
```python
import ndlib.VoterModel as m
```

Generate/load a graph with the [networkx](https://networkx.github.io/) library
```python
import networkx as nx
g = nx.erdos_renyi_graph(1000, 0.1)
```
Initialize the model on the graph
```python
model = m.VoterModel(g)
```
Set the nodel initial status
```python
model.set_initial_status({'model': {'percentage_infected': 0.2}})
```
Request a single iteration of the simulation
```python
it_id, it_status = model.iteration()
```
or a bunch of iterations
```python
it_bunch = model.iteration_bunch(bunch_size=10)
``` 

Each model can assing multiple statuses to nodes. In the implemented models we used the following convention:
```python
Blocked Nodes: -1 # Only: Kertesz Threshold
Susceptible: 0
Infected: 1
Removed: 2 # Only: SIR, Independent Cascades
```
One model (Cognitive Opinion Dynamics), due to his definition, employs real values in [0,1] as node statuses.

## Rationale behind the implemented models

- All models inherit from ndlib.DiffusionModel

- Model configuration and parameter settings is generalized by passing configuration dictionaries

- NDlib describes diffusion models as agent-based simulations occurring at discrete time: once configured the desired model and selected the target network, subsequent iterations will provide to the user the current status of each node.

- At each iterations are returned only the nodes (and current status) that changed their previous configuration. 

### Model configuration
Every model needs few parameters to be executed, in order to make general the initialization and iterative steps we decided to describe model configuration via dictionaries. In particular to initialize the implemented models you must supply (the chosen values are only examples of possible configurations):
```python
model = m.SznajdModel(g)
model = m.VoterModel(g) 
model = m.QVoterModel(g, {'q': 5})
model = m.CognitiveOpDynModel(g,{'I':0.15,'B_range_min':0, 'B_range_max':1,'T_range_min':0,'T_range_max':1,'R_fraction_negative':1/3.0,'R_fraction_neutral':1/3.0,'R_fraction_positive':1/3.0})
model = m.IndependentCascadesModel(g) # needs edges threshold informations
model = m.ThresholdModel(g) # needs node threshold informations
model = m.ProfileModel(g)  # needs node profile informations
model = m.ProfileThresholdModel(g) # needs node profile and threshold informations
model = m.SIModel(g, {'beta': 0.1})
model = m.SIRModel(g, {'beta': 0.1, 'gamma': 0.1})
model = m.SISModel(g, {'beta': 0.1, 'lambda': 0.1})
model = m.KerteszThresholdModel(g, {'adopter_rate': 0.1, 'blocked': 0.1}) # needs node threshold informations
```
All parameters are specified within each method description.

Moreover, additional parameters can be specified to define the initial configuration of the network by using the set_initial_status method.
In particular it takes as input a (not necessarely full defined) dictionary having the following form:
```python
{
 'nodes': {'threshold': {}, 'profile': {}},
 'edges': {},
 'model': {'percentage_infected': 0, 'infected_nodes': []}
}
```
where:
- the 'nodes' component describes the individual values of (all) node thresholds and/or profiles i.e.
```python
{'nodes':{ 'threshold': {node1: value1, node2: value2, node3: value3},
          'profile': {node1: value1, node2: value2, node3: value3}}
```
- the 'edges' component describes the edge weights i.e.
```python
{'edges': [
            {'source': node1, 'target': node2, 'weight': value},
            {'source': node2, 'target': node3, 'weight': value}
           ]}
```
- the 'model' component define either the percentage of initial nodes (selected at random) or a specific initial set of infected nodes. In case both 'percentage_infected' and 'infected_nodes' are specified the latter is ignored.

## Implement new models
Implement additional models is simple since it only requires to define a class that:
- implement the partial abstract class ndlib.DiffusionModel
- implement the iteration() method specifying its agent-based rules 

### Structure Example
```python
from ndlib.DiffusionModel import DiffusionModel

class MyModel(DiffusionModel):
    
    def iteration(self):
    	
    	# if first iteration return the initial node status
        if self.actual_iteration == 0:
            self.actual_iteration += 1
        return 0, self.status
    
        actual_status = {node: nstatus for node, nstatus in self.status.iteritems()}
        for u in self.graph.nodes():
            # evluate possible status changes using the model parameters (accessible via self.params)
            # e.g. self.params['beta'], self.param['nodes']['threshold'][u], self.params['edges'][(id_node0, idnode1)]
        
        # identify the changes w.r.t. previous iteration
        delta = self.status_delta(actual_status)
        # update the actual status and iterative step
        self.status = actual_status
        self.actual_iteration += 1
        
        # return the actual configuration (only nodes with status updates)
        return self.actual_iteration - 1, delta
```
If you like to include your model in NDlib (as well as in [NDlib-REST](https://github.com/GiulioRossetti/ndlib-rest)) open an issue and contact us.
