****************
Algorithmic Bias
****************

.. note:: The Algorithmic Bias model will be officially released in NDlib 4.0.1

--------
Statuses
--------

Node statuses are continuous values in [0,1].

----------
Parameters
----------

===================  =====  ================  =======  =========  =============================================
Name                 Type   Value Type        Default  Mandatory  Description
===================  =====  ================  =======  =========  =============================================
epsilon              Model  float in [0, 1]            True       Bounded confidence threshold
gamma                Model  int in [0, 100]            True       Algorithmic bias
===================  =====  ================  =======  =========  =============================================


-------
Methods
-------

The following class methods are made available to configure, describe and execute the simulation:

^^^^^^^^^
Configure
^^^^^^^^^

.. autoclass:: ndlib.models.opinions.AlgorithmicBiasModel.AlgorithmicBiasModel
.. automethod:: ndlib.models.opinions.AlgorithmicBiasModel.AlgorithmicBiasModel.__init__(graph)

.. automethod:: ndlib.models.opinions.AlgorithmicBiasModel.AlgorithmicBiasModel.set_initial_status(self, configuration)
.. automethod:: ndlib.models.opinions.AlgorithmicBiasModel.AlgorithmicBiasModel.reset(self)

^^^^^^^^
Describe
^^^^^^^^

.. automethod:: ndlib.models.opinions.AlgorithmicBiasModel.AlgorithmicBiasModel.get_info(self)
.. automethod:: ndlib.models.opinions.AlgorithmicBiasModel.AlgorithmicBiasModel.get_status_map(self)

^^^^^^^^^^^^^^^^^^
Execute Simulation
^^^^^^^^^^^^^^^^^^
.. automethod:: ndlib.models.opinions.AlgorithmicBiasModel.AlgorithmicBiasModel.iteration(self)
.. automethod:: ndlib.models.opinions.AlgorithmicBiasModel.AlgorithmicBiasModel.iteration_bunch(self, bunch_size)


-------
Example
-------

In the code below is shown an example of instantiation and execution of a AlgorithmicBiasModel model simulation on a random graph: we set the initial infected node set to the 10% of the overall population.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions.AlgorithmicBiasModel as ab

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = ab.AlgorithmicBiasModel(g)

    # Model configuration
    config = mc.Configuration()
    config.add_model_parameter("epsilon", 0.32)
    config.add_model_parameter("gamma", 1)
    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


