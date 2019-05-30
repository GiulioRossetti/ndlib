.. _model_conf:

***********
ModelConfig
***********

The ``ModelConfig`` object is the common interface used to set up simulation experiments.


.. autoclass:: ndlib.models.ModelConfig.Configuration

It allows to specify four categories of experiment configurations:

1. Model configuration
2. Node Configuration
3. Edge Configuration
4. Initial Status

Every diffusion model has its own parameters (as defined in its reference page).


-------------------
Model Configuration
-------------------

Model configuration involves the instantiation of both the *mandatory* and *optional* parameters of the chosen diffusion model.

.. automethod:: ndlib.models.ModelConfig.Configuration.add_model_parameter(self, param_name, param_value)

Model parameters can be setted as in the following example:

.. code-block:: python

    import ndlib.models.ModelConfig as mc

    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter("beta", 0.15)

The only model parameter common to all the diffusive approaches is ``fraction_infected`` that allows to specify the ratio of infected nodes at the beginning of the simulation.


------------------
Node Configuration
------------------

Node configuration involves the instantiation of both the *mandatory* and *optional* parameters attached to individual nodes.

.. automethod:: ndlib.models.ModelConfig.Configuration.add_node_configuration(self, param_name, node_id, param_value)
.. automethod:: ndlib.models.ModelConfig.Configuration.add_node_set_configuration(self, param_name, node_to_value)


Node parameters can be set as in the following example:

.. code-block:: python

    import ndlib.models.ModelConfig as mc

    # Model Configuration
    config = mc.Configuration()

    threshold = 0.25
    for i in g.nodes():
        config.add_node_configuration("threshold", i, threshold)


------------------
Edge Configuration
------------------

Edge configuration involves the instantiation of both the *mandatory* and *optional* parameters attached to individual edges.


.. automethod:: ndlib.models.ModelConfig.Configuration.add_edge_configuration(self, param_name, edge, param_value)
.. automethod:: ndlib.models.ModelConfig.Configuration.add_edge_set_configuration(self, param_name, edge_to_value)


Edge parameters can be set as in the following example:

.. code-block:: python

    import ndlib.models.ModelConfig as mc

    # Model Configuration
    config = mc.Configuration()

    threshold = 0.25
    for i in g.nodes():
        config.add_edge_configuration("threshold", i, threshold)


--------------------
Status Configuration
--------------------

Status configuration allows to specify explicitly the status of a set of nodes at the beginning of the simulation.


.. automethod:: ndlib.models.ModelConfig.Configuration.add_model_initial_configuration(self, status_name, nodes)

Node statuses can be set as in the following example:

.. code-block:: python

    import ndlib.models.ModelConfig as mc

    # Model Configuration
    config = mc.Configuration()

    infected_nodes = [0, 1, 2, 3, 4, 5]
    config.add_model_initial_configuration("Infected", infected_nodes)

Explicit status specification takes priority over the percentage specification expressed via model definition (e.g. ``fraction_infected``).

Only the statuses implemented by the chosen model can be used to specify initial configurations of nodes.
