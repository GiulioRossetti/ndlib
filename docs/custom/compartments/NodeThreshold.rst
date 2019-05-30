**************
Node Threshold
**************

Node Threshold compartments are used to evaluate deterministic events attached to network nodes.

Consider the transition rule **Susceptible->Infected** that requires at least a percentage *beta* of
*Infected* neighbors for a node *n* to be satisfied.

Such rule can be described by a simple compartment that models Node Threshold behaviors. Let's call il *NT*.

The rule will take as input the *initial* node status (Susceptible), the *final* one (Infected) and the *NT* compartment.
*NT* will thus require a threshold (*beta*) of activation and a *triggering* status.

During each rule evaluation, given a node *n*

- if the actual status of *n* equals the rule *initial* one
    - let *b* identify the ratio of *n* neighbors in the *triggering* status
    - if *b >= beta* then *NS* is considered *satisfied* and the status of *n* changes from *initial* to *final*.


----------
Parameters
----------

=================  ===============  =======  =========  =====================
Name               Value Type       Default  Mandatory  Description
=================  ===============  =======  =========  =====================
threshold          float in [0, 1]           False      Node threshold
triggering_status  string           None     True       Trigger
=================  ===============  =======  =========  =====================

-------
Example
-------

In the code below is shown the formulation of a Threshold model using NodeThreshold compartments.

The compartment, *c1*, is used to implement the transition rule *Susceptible->Infected*.
It requires a threshold - here set equals to 0.2.

.. code-block:: python

	import networkx as nx
	import ndlib.models.ModelConfig as mc
	import ndlib.models.CompositeModel as gc
	import ndlib.models.compartments.NodeThreshold as ns

	# Network generation
	g = nx.erdos_renyi_graph(1000, 0.1)

	# Composite Model instantiation
	model = gc.CompositeModel(g)

	# Model statuses
	model.add_status("Susceptible")
	model.add_status("Infected")

	# Compartment definition
	c1 = ns.NodeThreshold(0.1, triggering_status="Infected")

	# Rule definition
	model.add_rule("Susceptible", "Infected", c1)

	# Model initial status configuration
	config = mc.Configuration()
	config.add_model_parameter('fraction_infected', 0.1)

	# Simulation execution
	model.set_initial_status(config)
	iterations = model.iteration_bunch(100)

In case of an heterogeneous node threshold distribution the same model can be expressed as follows

.. code-block:: python

	import networkx as nx
	import ndlib.models.ModelConfig as mc
	import ndlib.models.CompositeModel as gc
	import ndlib.models.compartments.NodeThreshold as ns

	# Network generation
	g = nx.erdos_renyi_graph(1000, 0.1)

	# Composite Model instantiation
	model = gc.CompositeModel(g)

	# Model statuses
	model.add_status("Susceptible")
	model.add_status("Infected")

	# Compartment definition
	c1 = ns.NodeThreshold(triggering_status="Infected")

	# Rule definition
	model.add_rule("Susceptible", "Infected", c1)

	# Model initial status configuration
	config = mc.Configuration()

	# Threshold specs
	for i in g.nodes():
		config.add_node_configuration("threshold", i, np.random.random_sample())

	config = mc.Configuration()
	config.add_model_parameter('fraction_infected', 0.1)

	# Simulation execution
	model.set_initial_status(config)
	iterations = model.iteration_bunch(100)

