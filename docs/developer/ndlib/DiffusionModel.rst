**************************
Describe a Diffusion Model
**************************

All the diffusion models implemented in ``NDlib`` extends the abstract class ``ndlib.models.DiffusionModel``.

.. autoclass:: ndlib.models.DiffusionModel.DiffusionModel

Such class implements the logic behind model construction, configuration and execution.

In order to describe a novel diffusion algorithm the following steps must be followed:

-----------------
Model Description
-----------------

As convention a new model should be described in a python file named after it, e.g. a ``MyModule`` class should be implemented in a ``MyModule.py`` file.

.. automethod:: ndlib.models.DiffusionModel.DiffusionModel.__init__(self, graph)

In oder to effectively describe the model the ``__init__`` function of ``ndlib.models.DiffusionModel`` must be specified as follows:

.. code-block:: python

	from ndlib.models.DiffusionModel import DiffusionModel

	class MyModel(DiffusionModel):

		def __init__(self, graph):

			# Call the super class constructor
			super(self.__class__, self).__init__(graph)

			# Method name
			self.name = "MyModel"

			# Available node statuses
			self.available_statuses = {
				"Status_0": 0,
				"Status_1": 1
			}
			# Exposed Parameters
			self.parameters = {
				"model":
	  				"parameter_name": {
	     					"descr": "Description 1"
	     					"range": [0,1],
	     					"optional": False
	   					},
					},
				"nodes":
					"node_parameter_name": {
	     					"descr": "Description 2"
	     					"range": [0,1],
	     					"optional": True
	   					},
					},
				"edges":
					"edge_parameter_name": {
							"descr": "Description 3"
							"range": [0,1],
							"optional": False
						},
					},
				}

In the ``__init__`` methods three components are used to completely specify the model:

- ``self.name``: its **name**;
- ``self.available_statuses``: the node **statuses** it allows along with an associated numerical code;
- ``self.parameters``: the **parameters** it requires, their range, description and optionality.

All those information will be used to check the user provided configurations as well as metadata for visualizations.

--------------
Iteration Rule
--------------

Once described the model metadata it is necessary to provide the agent-based description of its general iteration-step.

.. automethod:: ndlib.models.DiffusionModel.DiffusionModel.iteration(self)

To do so, the ``iteration()`` method of the base class has to be overridden in ``MyModel`` as follows:

.. code-block:: python

	def iteration(self):

		# Set initial node statuses
		actual_status = {node: nstatus for node, nstatus in self.status.items()}

		# first iteration
		if self.actual_iteration == 0:
			self.actual_iteration += 1
			return 0, actual_status

		# iteration inner loop
		for u in self.graph.nodes():
			# Iteration updates

		# Incremental result
		delta = self.status_delta(actual_status)
		self.status = actual_status
		self.actual_iteration += 1

		return self.actual_iteration - 1, delta

The provided template is composed by 4 steps:

1. making a copy of the actual diffusion status;
2. first iteration handling: if present the model returns as result of the first iteration is initial status;
3. iteration loop: definition, and application, of the rules that regulates individual node status transitions;
4. construction of the incremental result.

All the steps are mandatory in order to assure a consistent behaviour across different models

All the user specified parameters (models as well as nodes and edges ones) can be used within the ``iteration()`` method: to access them an internal data structure is provided, ``self.params``.

``self.params`` is a dictionary that collects all the passed values using the following notation:

- Model parameters: ``self.params['model']['parameter_name']``
- Node parameters: ``self.param['nodes']['nodes_parameter'][node_id]``
- Edge parameters: ``self.param['edges']['edges_parameter'][(node_id1, node_id2)]``

Within the iteration loop the node status updates must be made on the ``actual_status`` data structure, e.g. the copy made during Step 1.

Each iteration returns the **incremental** status of the diffusion process as well as the iteration **progressive number**.