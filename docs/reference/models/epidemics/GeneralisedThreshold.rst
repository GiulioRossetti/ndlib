*********************
Generalised Threshold
*********************

--------
Statuses
--------

During the simulation a node can experience the following statuses:

===========  ====
Name         Code
===========  ====
Susceptible  0
Infected     1
===========  ====

----------
Parameters
----------

=========  =====  ===============  =======  =========  ========================
Name       Type   Value Type       Default  Mandatory  Description
=========  =====  ===============  =======  =========  ========================
threshold  Node   float in [0, 1]  0.1      False      Individual threshold
tau        Model  int                       True       Adoption threshold rate
mu         Model  int                       True       Exogenous timescale
=========  =====  ===============  =======  =========  ========================



The initial infection status can be defined via:

    - **percentage_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

The two options are mutually exclusive and the latter takes precedence over the former.

-------
Methods
-------

The following class methods are made available to configure, describe and execute the simulation:

^^^^^^^^^
Configure
^^^^^^^^^
.. autoclass:: ndlib.models.epidemics.GeneralisedThresholdModel.GeneralisedThresholdModel
.. automethod:: ndlib.models.epidemics.GeneralisedThresholdModel.GeneralisedThresholdModel.__init__(graph)

.. automethod:: ndlib.models.epidemics.GeneralisedThresholdModel.GeneralisedThresholdModel.set_initial_status(self, configuration)
.. automethod:: ndlib.models.epidemics.GeneralisedThresholdModel.GeneralisedThresholdModel.reset(self)

^^^^^^^^
Describe
^^^^^^^^

.. automethod:: ndlib.models.epidemics.GeneralisedThresholdModel.GeneralisedThresholdModel.get_info(self)
.. automethod:: ndlib.models.epidemics.GeneralisedThresholdModel.GeneralisedThresholdModel.get_status_map(self)

^^^^^^^^^^^^^^^^^^
Execute Simulation
^^^^^^^^^^^^^^^^^^
.. automethod:: ndlib.models.epidemics.GeneralisedThresholdModel.GeneralisedThresholdModel.iteration(self)
.. automethod:: ndlib.models.epidemics.GeneralisedThresholdModel.GeneralisedThresholdModel.iteration_bunch(self, bunch_size)


-------
Example
-------

In the code below is shown an example of instantiation and execution of a Threshold model simulation on a random graph: we set the initial set of infected nodes as 1% of the overall population, and assign a threshold of 0.25 to all the nodes.


.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics.GeneralisedThresholdModel as gth

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = gth.GeneralisedThresholdModel(g)
        
    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter('percentage_infected', 0.1)
    config.add_model_parameter('tau', 5)
    config.add_model_parameter('mu', 5)

    # Setting node parameters
    threshold = 0.25
    for i in g.nodes():
        config.add_node_configuration("threshold", i, threshold)

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


