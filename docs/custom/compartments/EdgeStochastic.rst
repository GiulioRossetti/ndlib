***************
Edge Stochastic
***************

Edge Stochastic compartments are used to evaluate stochastic events attached to network edges.

Consider the transition rule **Susceptible->Infected** that, to be triggered, requires a direct link among an infected node and a susceptible one.
Moreover, it can happens subject to probability *beta*, a parameter tied to the specific edge connecting the two nodes.
Such rule can be described by a simple compartment that models Edge Stochastic behaviors. Let's call il *ES*.

The rule will take as input the *initial* node status (Susceptible), the *final* one (Infected) and the *ES* compartment.
*ES* will thus require a probability (*beta*) of edge activation and a *triggering* status.
In advanced scenarios, where the probability threshold vary from edge to edge, it is possible to specify it using the model configuration object.

During each rule evaluation, given a node *n* and one of its neighbors *m*

- if the actual status of *n* equals the rule *initial* one and the one of *m* equals the *triggering* one
	- a random value *b* in [0,1] will be generated
	- if *b <= beta* then *ES* is considered *satisfied* and the status of *n* changes from *initial* to *final*.


----------
Parameters
----------

=================  ===============  =======  =========  =====================
Name               Value Type       Default  Mandatory  Description
=================  ===============  =======  =========  =====================
threshold          float in [0, 1]  1/N      True       Event probability
triggering_status  string           None     False      Trigger
=================  ===============  =======  =========  =====================

Where N is the number of nodes in the graph.

-------
Example
-------

In the code below is shown the formulation of a Cascade model using EdgeStochastic compartments.

The compartment, *c1*, is used to implement the transition rule *Susceptible->Infected*.
It requires a probability threshold - here set equals to 0.02 - and restrain the rule evaluation to all those nodes that have at least an Infected neighbors.


.. code-block:: python

	import networkx as nx
	import ndlib.models.ModelConfig as mc
	import ndlib.models.CompositeModel as gc
	import ndlib.models.compartments.EdgeStochastic as es

	# Network generation
	g = nx.erdos_renyi_graph(1000, 0.1)

	# Composite Model instantiation
	model = gc.CompositeModel(g)

	# Model statuses
	model.add_status("Susceptible")
	model.add_status("Infected")
	model.add_status("Removed")

	# Compartment definition
	c1 = ns.EdgeStochastic(0.02, triggering_status="Infected")

	# Rule definition
	model.add_rule("Susceptible", "Infected", c1)

	# Model initial status configuration
	config = mc.Configuration()
	config.add_model_parameter('fraction_infected', 0.1)

	# Simulation execution
	model.set_initial_status(config)
	iterations = model.iteration_bunch(100)


In case of an heterogeneous edge threshold distribution the same model can be expressed as follows

.. code-block:: python

	import networkx as nx
	import ndlib.models.ModelConfig as mc
	import ndlib.models.CompositeModel as gc
	import ndlib.models.compartments.EdgeStochastic as es

	# Network generation
	g = nx.erdos_renyi_graph(1000, 0.1)

	# Composite Model instantiation
	model = gc.CompositeModel(g)

	# Model statuses
	model.add_status("Susceptible")
	model.add_status("Infected")
	model.add_status("Removed")

	# Compartment definition
	c1 = es.EdgeStochastic(triggering_status="Infected")

	# Rule definition
	model.add_rule("Susceptible", "Infected", c1)


	# Model initial status configuration
	config = mc.Configuration()

	# Threshold specs
	for e in g.edges():
		config.add_edge_configuration("threshold", e, np.random.random_sample())

	config = mc.Configuration()
	config.add_model_parameter('fraction_infected', 0.1)

	# Simulation execution
	model.set_initial_status(config)
	iterations = model.iteration_bunch(100)

