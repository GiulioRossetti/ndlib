****
SWIR
****


--------
Statuses
--------

During the simulation a node can experience the following statuses:

===========  ====
Name         Code
===========  ====
Susceptible  0
Infected     1
Weakened	 2
Removed      3
===========  ====

----------
Parameters
----------

=====  =====  ===============  =======  =========  =====================
Name   Type   Value Type       Default  Mandatory  Description
=====  =====  ===============  =======  =========  =====================
kappa  Model  float in [0, 1]           True
mu     Model  float in [0, 1]           True
nu     Model  float in [0, 1]           True
=====  =====  ===============  =======  =========  =====================

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
.. autoclass:: ndlib.models.epidemics.SWIRModel.SWIRModel
.. automethod:: ndlib.models.epidemics.SWIRModel.SWIRModel.__init__(graph)

.. automethod:: ndlib.models.epidemics.SWIRModel.SWIRModel.set_initial_status(self, configuration)
.. automethod:: ndlib.models.epidemics.SWIRModel.SWIRModel.reset(self)

^^^^^^^^
Describe
^^^^^^^^

.. automethod:: ndlib.models.epidemics.SWIRModel.SWIRModel.get_info(self)
.. automethod:: ndlib.models.epidemics.SWIRModel.SWIRModel.get_status_map(self)

^^^^^^^^^^^^^^^^^^
Execute Simulation
^^^^^^^^^^^^^^^^^^
.. automethod:: ndlib.models.epidemics.SWIRModel.SWIRModel.iteration(self)
.. automethod:: ndlib.models.epidemics.SWIRModel.SWIRModel.iteration_bunch(self, bunch_size)


-------
Example
-------

In the code below is shown an example of instantiation and execution of an SEIR simulation on a random graph: we set the initial set of infected nodes as % of the overall population, a probability of infection of 1%, a removal probability of 0.5% and an incubation period of 5% (e.g. 20 iterations).

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics.SWIRModel as swir

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = swir.SWIRModel(g)

    # Model Configuration
    cfg = mc.Configuration()
    cfg.add_model_parameter('kappa', 0.01)
    cfg.add_model_parameter('mu', 0.005)
    cfg.add_model_parameter('nu', 0.05)
    cfg.add_model_parameter("percentage_infected", 0.05)
    model.set_initial_status(cfg)

    # Simulation execution
    iterations = model.iteration_bunch(200)


