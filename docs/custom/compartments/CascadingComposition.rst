*********************
Cascading Composition
*********************

Since each compartment identifies an atomic condition it is natural to imagine rules described as *chains* of compartments.

A compartment chain identify and ordered set of conditions that needs to be satisfied to allow status transition (it allows describing an **AND** logic).

To implement such behaviour each compartment exposes a parameter (named *composed*) that allows to specify the subsequent compartment to evaluate in case it condition is satisfied.

-------
Example
-------

In the code below is shown the formulation of a model implementing cascading compartment composition.

The rule **Susceptible->Infected** is implemented using three NodeStochastic compartments chained as follows:

	- If the node *n* is *Susceptible*
		- *c1*: if at least a neighbor of the actual node is *Infected*, with probability 0.5 evaluate compartment *c2*
		- *c2*: with probability 0.4 evaluate compartment *c3*
		- *c3*: with probability 0.2 allow the transition to the *Infected* state

Indeed, heterogeneous compartment types can be mixed to build more complex scenarios.

.. code-block:: python

	import networkx as nx
	import ndlib.models.ModelConfig as mc
	import ndlib.models.CompositeModel as gc
	import ndlib.models.compartments as cpm
	from ndlib.models.compartments.enums.NumericalType import NumericalType

	# Network generation
	g = nx.erdos_renyi_graph(1000, 0.1)

	# Composite Model instantiation
	model = gc.CompositeModel(g)

	# Model statuses
	model.add_status("Susceptible")
	model.add_status("Infected")

	# Compartment definition and chain construction
	c3 = cpm.NodeStochastic(0.2)
	c2 = cpm.NodeStochastic(0.4, composed=c3)
	c1 = cpm.NodeStochastic(0.5, "Infected", composed=c2)

	# Rule definition
	model.add_rule("Susceptible", "Infected", c1)

	# Model initial status configuration
	config = mc.Configuration()
	config.add_model_parameter('fraction_infected', 0.1)

	# Simulation execution
	model.set_initial_status(config)
	iterations = model.iteration_bunch(100)
