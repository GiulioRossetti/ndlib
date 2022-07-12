************************
Edge Numerical Attribute
************************

Edge Numerical Attribute compartments are used to evaluate events attached to numeric edge attributes.

Consider the transition rule **Susceptible->Infected** that requires a that the susceptible node is connected to a neighbor
through a link expressing a specific value of an internal numeric attribute, *attr*, to be satisfied (e.g. "weight">=3).
Such rule can be described by a simple compartment that models Edge Numerical Attribute selection. Let's call il *ENA*.

The rule will take as input the *initial* node status (Susceptible), the *final* one (Infected) and the *ENA* compartment.
*ENA* will thus require a probability (*beta*) of activation.

During each rule evaluation, given a node *n* and one of its neighbors *m*

- if the actual status of *n* equals the rule *initial*
    - if *attr(n,m)* **op** *attr*
    - a random value *b* in [0,1] will be generated
    - if *b <= beta*, then *ECA* is considered *satisfied* and the status of *n* changes from *initial* to *final*.

**op** represent a logic operator and can assume one of the following values:
- equality: "=="
- less than: "<"
- greater than: ">"
- equal or less than: "<="
- equal or greater than: ">="
- not equal to: "!="
- within: "IN"

Moreover, *ENA* allows to specify a *triggering* status in order to restrain the compartment evaluation to those nodes that:

1. match the rule *initial* state, and
2. have at least one neighbors in the *triggering* status.


----------
Parameters
----------

=================  ===============  =======  =========  =======================
Name               Value Type       Default  Mandatory  Description
=================  ===============  =======  =========  =======================
attribute          string           None     True       Attribute name
value              numeric(*)       None     True       Attribute testing value
op                 string           None     True       Logic operator
probability        float in [0, 1]  1        False      Event probability
triggering_status  string           None     False      Trigger
=================  ===============  =======  =========  =======================

(*) When *op* equals "IN" the attribute *value* is expected to be a tuple of two elements identifying a closed interval.

-------
Example
-------

In the code below is shown the formulation of a model using EdgeNumericalAttribute compartments.

The first compartment, *c1*, is used to implement the transition rule *Susceptible->Infected*.
It restrain the rule evaluation to all those nodes connected at least to a neighbor through a link having "weight" equals to 4.

The second compartment, *c2*, is used to implement the transition rule *Infected->Recovered*.
It restrain the rule evaluation to all those nodes connected at least to a "Susceptible" neighbor through a link having "weight" in the range [3, 6].


.. code-block:: python

	import networkx as nx
	import random
	import ndlib.models.ModelConfig as mc
	import ndlib.models.CompositeModel as gc
	import ndlib.models.compartments.EdgeNumericalAttribute as na

	# Network generation
	g = nx.erdos_renyi_graph(1000, 0.1)

	# Setting edge attribute
	attr = {(u, v): {"weight": int((u+v) % 10)} for (u, v) in g.edges()}
	nx.set_edge_attributes(g, attr)

	# Composite Model instantiation
	model = gc.CompositeModel(g)

	# Model statuses
	model.add_status("Susceptible")
	model.add_status("Infected")
	model.add_status("Removed")

	# Compartment definition
	c1 = na.EdgeNumericalAttribute("weight", value=4, op="==", probability=0.6)
	c2 = na.EdgeNumericalAttribute("weight", value=(3, 6), op="IN", probability=0.6, triggering_status="Susceptible")

	# Rule definition
	model.add_rule("Susceptible", "Infected", c1)
	model.add_rule("Infected", "Recovered", c2)

	# Model initial status configuration
	config = mc.Configuration()
	config.add_model_parameter('fraction_infected', 0)

	# Simulation execution
	model.set_initial_status(config)
	iterations = model.iteration_bunch(100)
