================
Continuous Model
================

.. Warning::

    ``ContinuousModel`` requires python3

The composite model only supports discrete states, but more advanced custom models might require continuous states and more options.
The general manner of creating a model remains the same as the ``CompositeModel``, but it allows for configuration by adding (optional) extra steps.

The general modeling flow is as follows:

	1. Define a graph
	2. Add (continuous) internal states
	3. Define constants and intial values
	4. Create update conditions
	5. Add iteration schemes (optional)
	6. Simulate
	7. Optional steps(Visualize/Sensitivity analysis)

------------------------------------
Graph, internal states and constants
------------------------------------

The graphs should still be ``Networkx`` graphs, either defined by yourself or generated using one of their built-in functions.
Attributes in the graph can still be accessed and used to update functions.

After a graph is defined, the model can be initialized and internal states can be added to the model. When the model is initalized,
states can be added using ``add_status(status)`` function, where the `status` argument is a string.

If the model requires certain constant values, these can be added using the ``constants`` parameter when initializing the model.
It should be a dictionary where the key corresponds to the constant name and the value to the constant value.
Adding constants is completely optional.

Example:

.. code-block:: python

	import networkx as nx
	from ndlib.models.ContinuousModel import ContinuousModel

	g = nx.erdos_renyi_graph(n=1000, p=0.1)

	constants = {
		'constant_1': 0.1,
		'constant_2': 2.5
	}

	model = ContinuousModel(g, constants=constants)
	model.add_status('status1')
	model.add_status('status2')

-------------
Intial values
-------------

After the graph has been created, the model has been initalized, and the internal states have been added,
the next step is to define the intial values of the states.

This is done by creating a dictionary, that maps a state name to an initial value.
This value has to be a continous value, that can be statically set, or it can be a function that will be executed for every node.
If the value is a function, it should take the following arguments:

	- node: the current node for which the initial state is being set
	- graph: the full networkx graph containing all nodes
	- status: a dictionary that contains all the previously set state (str) -> value (number) mappings for that node
	- constants: the dictionary of specified constants, None if no constants are specified

After creating the dictionary, it can be added to the model using the ``set_initial_status(dict, config)`` function.
The config argument is  acquired by the ``Configuration()`` function from the ``ModelConfig`` class.

The example below will create a model with 3 states. Every node in the model will initialize `status_1` with a value returned by the `initial_status_1` function,
which will results in all nodes getting a random uniform value between 0 and 0.5. The same happens for the internal state `status_2`.
The third state is constant and thus the same for every node.

.. code-block:: python

	import networkx as nx
	import numpy as np
	from ndlib.models.ContinuousModel import ContinuousModel
	import ndlib.models.ModelConfig as mc

	def initial_status_1(node, graph, status, constants):
		return np.random.uniform(0, 0.5)

	def initial_status_2(node, graph, status, constants):
		return status['status_1'] + np.random.uniform(0.5, 1)

	initial_status = {
		'status_1': initial_status_1,
		'status_2': initial_status_2,
		'status_3': 2
	}

	g = nx.erdos_renyi_graph(n=1000, p=0.1)

	model = ContinuousModel(g)

	model.add_status('status_1')
	model.add_status('status_2')
	model.add_status('status_3')

	config = mc.Configuration()
	model.set_initial_status(initial_status, config)


-----------------
Update conditions
-----------------

Another important part of the model is creating conditions and update rules. This follows the same principle as using the compartments,
which have already been explained. Every update condition has a:

	- State: A string matching an internal state

	- Update function: A function that should be used to update the state if the condition is true. Its arguments are:

		- node: The number of the node that is currently updated
		- graph: The complete graph containing all the nodes
		- status: A status dictionary that maps a node to a dictionary with State -> Value mappings
		- attributes: The networkx attributes of the network
		- constants: The specified constants, None if not defined

	- Condition: A compartment condition (Node/Edge/Time)

	- Scheme (optional): An iteration scheme to specify the iteration number(s) and node(s)

In the example below, the states are updated when the condition ``NodeStochastic(1)`` is true, which is always the case, so the update functions are called every iteration.
Here the state `status_1` will be updated every iteration by setting it equal to `status_2` + 0.1. The same is done for `status_2`, but in this case it is set equal to `status_1` + 0.5.

.. code-block:: python

	import networkx as nx
	from ndlib.models.ContinuousModel import ContinuousModel
	import ndlib.models.ModelConfig as mc

	g = nx.erdos_renyi_graph(n=1000, p=0.1)

	model = ContinuousModel(g)

	model.add_status('status_1')
	model.add_status('status_2')

	# Compartments
	condition = NodeStochastic(1)

	# Update functions
	def update_1(node, graph, status, attributes, constants):
		return status[node]['status_2'] + 0.1

	def update_2(node, graph, status, attributes, constants):
		return status[node]['status_1'] + 0.5

	# Rules
	model.add_rule('status_1', update_1, condition)
	model.add_rule('status_2', update_2, condition)

-----------------
Iteration schemes
-----------------

Another addition to the model, are iteration schemes. These can be used for two things:

1. Specify nodes to update
2. Specify iteration range when updates should take place

This allows to only update a select amount of nodes during a specific time in the iteration.
Under the hood, when schemes are not defined,
a default scheme is used for every rule that is active during each iteration and selects all nodes.

To create a scheme, simply define a list where each element is a dictionary containing the following keys:

	- name: maps to a string that indicates the name of the scheme
	- function: maps to a function that returns the nodes that should be updated if a condition is true. Its arguments are:

		- graph: the full networkx graph
		- status: A status dictionary that maps a node to a dictionary with State -> Value mappings

	- lower (optional): maps to an integer indicating from which iteration the scheme should apply
	- upper (optional): maps to an integer indicating until which iteration the scheme should apply

After the scheme dictionary is created, it can be added to the model when the model is initalized:
``ContinuousModel(graph, constants=constants, iteration_schemes=schemes)``.

Furthermore, if rules are added using the ``add_rule`` function, it should now be done as follows:
``model.add_rule('state_name', update_function, condition, scheme_list)``.
Here a rule can be added to multiple schemes. The scheme_list is a list, where every element should match a name of a scheme,
which means that updates can be done in multiple schemes.
If a scheme_list is not provided, the rule will be executed for every iteration, for every node, if the condition is true.

In the example below, the previous model is executed in the same manner,
but this time, the update_1 function is only being evaluated when ``lower ≤ iteration < upper``,
in this case when the iterations are equal or bigger than 100 but lower than 200.
Furthermore, if the condition is true, the update function is then only executed for the nodes returned by the function specified in the scheme.
In this case a node is selected based on the weighted `status_1` value.
Because no scheme has been added to the second rule, it will be evaluated and executed for every node, each iteration.


.. code-block:: python

	import networkx as nx
	import numpy as np
	from ndlib.models.ContinuousModel import ContinuousModel
	import ndlib.models.ModelConfig as mc

	g = nx.erdos_renyi_graph(n=1000, p=0.1)

	# Define schemes
	def sample_state_weighted(graph, status):
		probs = []
		status_1 = [stat['status_1'] for stat in list(status.values())]
		factor = 1.0/sum(status_1)
		for s in status_1:
			probs.append(s * factor)
		return np.random.choice(graph.nodes, size=1, replace=False, p=probs)

	schemes = [
		{
		'name': 'random weighted agent',
		'function': sample_state_weighted,
		'lower': 100,
		'upper': 200
		}
	]

	model = ContinuousModel(g, iteration_schemes=schemes)

	model.add_status('status_1')
	model.add_status('status_2')

	# Compartments
	condition = NodeStochastic(1)

	# Update functions
	def update_1(node, graph, status, attributes, constants):
		return status[node]['status_2'] + 0.1

	def update_2(node, graph, status, attributes, constants):
		return status[node]['status_1'] + 0.5

	# Rules
	model.add_rule('status_1', update_1, condition, ['random weighted agent'])
	model.add_rule('status_2', update_2, condition)


----------
Simulation
----------

After everything has been specified and added to the model, it can be ran using the ``iteration_bunch(iterations)`` function.
It will run the model iterations amount of times and return the regular output as shown in other models before.

------------------------
Optional functionalities
------------------------

There are several extra configurations and options:

.. toctree::
   :maxdepth: 2

   optional/ModelRunner.rst
   optional/Visualization.rst

The ``ContinuousModelRunner`` can be used to simulate a model mutliple times using different parameters. 
It also includes sensitivity analysis functionalities.

The visualization section explains how visualizations can be configured, shown, and saved.

-------------------
Continuous examples
-------------------

Two examples have been added that reproduce models shown in two different papers.

.. toctree::
   :maxdepth: 2

   examples/ControlVsCraving.rst
   examples/HIOM.rst