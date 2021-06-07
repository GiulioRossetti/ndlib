**************************
Node Categorical Attribute
**************************

Node Categorical Attribute compartments are used to evaluate events attached to network nodes attributes.

Consider the transition rule **Susceptible->Infected** that requires a that the susceptible node express a specific value of an internal attribute, *attr*, to be satisfied (e.g. "Sex"="male").
Such rule can be described by a simple compartment that models Node Categorical Attribute selection. Let's call il *NCA*.

The rule will take as input the *initial* node status (Susceptible), the *final* one (Infected) and the *NCA* compartment.
*NCA* will thus require a probability (*beta*) of activation.

During each rule evaluation, given a node *n*

- if the actual status of *n* equals the rule *initial* one
	- a random value *b* in [0,1] will be generated
	- if *b <= beta* and *attr(n) == attr*, then *NCA* is considered *satisfied* and the status of *n* changes from *initial* to *final*.


----------
Parameters
----------

=================  ===============  =======  =========  =======================
Name               Value Type       Default  Mandatory  Description
=================  ===============  =======  =========  =======================
attribute          string           None     True       Attribute name
value              string           None     True       Attribute testing value
probability        float in [0, 1]  1        False      Event probability
=================  ===============  =======  =========  =======================

-------
Example
-------

In the code below is shown the formulation of a model using NodeCategoricalAttribute compartments.

The compartment, *c1*, is used to implement the transition rule *Susceptible->Infected*.
It restrain the rule evaluation to all those nodes for which the attribute "Sex" equals "male".

.. code-block:: python

	import networkx as nx
	import random
	import ndlib.models.ModelConfig as mc
	import ndlib.models.CompositeModel as gc
	import ndlib.models.compartments as cpm

	# Network generation
	g = nx.erdos_renyi_graph(1000, 0.1)

	# Setting node attribute
	attr = {n: {"Sex": random.choice(['male', 'female'])} for n in g.nodes()}
	nx.set_node_attributes(g, attr)

	# Composite Model instantiation
	model = gc.CompositeModel(g)

	# Model statuses
	model.add_status("Susceptible")
	model.add_status("Infected")
	model.add_status("Removed")

	# Compartment definition
	c1 = cpm.NodeCategoricalAttribute("Sex", "male", probability=0.6)

	# Rule definition
	model.add_rule("Susceptible", "Infected", c1)

	# Model initial status configuration
	config = mc.Configuration()
	config.add_model_parameter('fraction_infected', 0)

	# Simulation execution
	model.set_initial_status(config)
	iterations = model.iteration_bunch(100)
