***********************
Conditional Composition
***********************

Since each compartment identifies an atomic condition it is natural to imagine rules described as *trees* of compartments.

A compartment tree identify and ordered and disjoint set of conditions that needs to be satisfied to allow status transition (it allows describing an **OR** logic).

To implement such behaviour we implemented a ConditionalComposition compartment that allows to describe branching. Let's call it *CC*.

*CC* evaluate a *guard* compartment and, depending from the result it gets evaluate (True or False) move to the evaluation of one of its two *child* compartments.

----------
Parameters
----------

=================  ===============  =======  =========  =======================
Name               Value Type       Default  Mandatory  Description
=================  ===============  =======  =========  =======================
condition          Compartment      None     True       Guard Compartment
first_branch       Compartment      None     True       Positive Compartment
second_branch      Compartment      None     True       Negative Compartment
=================  ===============  =======  =========  =======================


-------
Example
-------

In the code below is shown the formulation of a model implementing conditional compartment composition.

The rule **Susceptible->Infected** is implemented using three NodeStochastic compartments chained as follows:

	- If the node *n* is *Susceptible*
		- *c1*: if at least a neighbor of the actual node is *Infected*, with probability 0.5 evaluate compartment *c2* else evaluate compartment *c3*
		- *c2*: with probability 0.2 allow the transition to the *Infected* state
		- *c3*: with probability 0.1 allow the transition to the *Infected* state

Indeed, heterogeneous compartment types can be mixed to build more complex scenarios.

.. code-block:: python

	import networkx as nx
	import ndlib.models.ModelConfig as mc
	import ndlib.models.CompositeModel as gc
	import ndlib.models.compartments as cpm
	from ndlib.models.compartments.enums.NumericalType import NumericalType
	import ndlib.models.compartments.ConditionalComposition as cif

	# Network generation
	g = nx.erdos_renyi_graph(1000, 0.1)

	# Composite Model instantiation
	model = gc.CompositeModel(g)

	# Model statuses
	model.add_status("Susceptible")
	model.add_status("Infected")

	# Compartment definition
	c1 = cpm.NodeStochastic(0.5, "Infected")
	c2 = cpm.NodeStochastic(0.2)
	c3 = cpm.NodeStochastic(0.1)

	# Conditional Composition
	cc = cif.ConditionalComposition(c1, c2, c3)

	# Rule definition
	model.add_rule("Susceptible", "Infected", cc)

	# Model initial status configuration
	config = mc.Configuration()
	config.add_model_parameter('fraction_infected', 0.1)

	# Simulation execution
	model.set_initial_status(config)
	iterations = model.iteration_bunch(100)
