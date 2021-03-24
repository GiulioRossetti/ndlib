***************
Node Stochastic
***************

Node Stochastic compartments are used to evaluate stochastic events attached to network nodes.

Consider the transition rule **Susceptible->Infected** that requires a probability *beta* to be satisfied.
Such rule can be described by a simple compartment that models Node Stochastic behaviors. Let's call il *NS*.

The rule will take as input the *initial* node status (Susceptible), the *final* one (Infected) and the *NS* compartment.
*NS* will thus require a probability (*beta*) of activation.

During each rule evaluation, given a node *n*

- if the actual status of *n* equals the rule *initial* one
	- a random value *b* in [0,1] will be generated
	- if *b <= beta* then *NS* is considered *satisfied* and the status of *n* changes from *initial* to *final*.

Moreover, *NS* allows to specify a *triggering* status in order to restrain the compartment evaluation to those nodes that:

1. match the rule *initial* state, and
2. have at least one neighbors in the *triggering* status.


----------
Parameters
----------

=================  ===============  =======  =========  =====================
Name               Value Type       Default  Mandatory  Description
=================  ===============  =======  =========  =====================
ratio              float in [0, 1]           True       Event probability
triggering_status  string           None     False      Trigger
=================  ===============  =======  =========  =====================

-------
Example
-------

In the code below is shown the formulation of a SIR model using NodeStochastic compartments.

The first compartment, *c1*, is used to implement the transition rule *Susceptible->Infected*.
It requires a probability threshold - here set equals to 0.02 - and restrain the rule evaluation to all those nodes that have at least an Infected neighbors.

The second compartment, *c2*, is used to implement the transition rule *Infected->Removed*.
Since such transition is not tied to neighbors statuses the only parameter required by the compartment is the probability of transition.

.. code-block:: python

	import networkx as nx
	import ndlib.models.ModelConfig as mc
	import ndlib.models.CompositeModel as gc
	import ndlib.models.compartments as cpm

	# Network generation
	g = nx.erdos_renyi_graph(1000, 0.1)

	# Composite Model instantiation
	model = gc.CompositeModel(g)

	# Model statuses
	model.add_status("Susceptible")
	model.add_status("Infected")
	model.add_status("Removed")

	# Compartment definition
	c1 = cpm.NodeStochastic(0.02, triggering_status="Infected")
	c2 = cpm.NodeStochastic(0.01)

	# Rule definition
	model.add_rule("Susceptible", "Infected", c1)
	model.add_rule("Infected", "Removed", c2)

	# Model initial status configuration
	config = mc.Configuration()
	config.add_model_parameter('fraction_infected', 0.1)

	# Simulation execution
	model.set_initial_status(config)
	iterations = model.iteration_bunch(100)
