****
SEIR
****

 
In the SEIR model [#]_, during the course of an epidemics, a node is allowed to change its status  from **Susceptible** (S) to **Exposed** (E) to **Infected** (I), then to **Removed** (R).

The model is instantiated on a graph having a non-empty set of infected nodes.

SEIR assumes that if, during a generic iteration, a susceptible node comes into contact with an infected one, it becomes infected after an exposition period with probability beta, than it can switch to removed with probability gamma (the only transition allowed are S→E→I→R).


--------
Statuses
--------

During the simulation a node can experience the following statuses:

===========  ====
Name         Code
===========  ====
Susceptible  0
Infected     1
Exposed		 2
Removed      3
===========  ====

----------
Parameters
----------

=====  =====  ===============  =======  =========  =====================
Name   Type   Value Type       Default  Mandatory  Description
=====  =====  ===============  =======  =========  =====================
beta   Model  float in [0, 1]           True       Infection probability
gamma  Model  float in [0, 1]           True       Removal probability
alpha  Model  float in [0, 1]           True       Incubation period
=====  =====  ===============  =======  =========  =====================

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

The two options are mutually exclusive and the latter takes precedence over the former.

-------
Methods
-------

The following class methods are made available to configure, describe and execute the simulation:

^^^^^^^^^
Configure
^^^^^^^^^
.. autoclass:: ndlib.models.epidemics.SEIRModel.SEIRModel
.. automethod:: ndlib.models.epidemics.SEIRModel.SEIRModel.__init__(graph)

.. automethod:: ndlib.models.epidemics.SEIRModel.SEIRModel.set_initial_status(self, configuration)
.. automethod:: ndlib.models.epidemics.SEIRModel.SEIRModel.reset(self)

^^^^^^^^
Describe
^^^^^^^^

.. automethod:: ndlib.models.epidemics.SEIRModel.SEIRModel.get_info(self)
.. automethod:: ndlib.models.epidemics.SEIRModel.SEIRModel.get_status_map(self)

^^^^^^^^^^^^^^^^^^
Execute Simulation
^^^^^^^^^^^^^^^^^^
.. automethod:: ndlib.models.epidemics.SEIRModel.SEIRModel.iteration(self)
.. automethod:: ndlib.models.epidemics.SEIRModel.SEIRModel.iteration_bunch(self, bunch_size)


-------
Example
-------

In the code below is shown an example of instantiation and execution of an SEIR simulation on a random graph: we set the initial set of infected nodes as % of the overall population, a probability of infection of 1%, a removal probability of 0.5% and an incubation period of 5% (e.g. 20 iterations).

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as ep

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = ep.SEIRModel(g)

    # Model Configuration
    cfg = mc.Configuration()
    cfg.add_model_parameter('beta', 0.01)
    cfg.add_model_parameter('gamma', 0.005)
    cfg.add_model_parameter('alpha', 0.05)
    cfg.add_model_parameter("fraction_infected", 0.05)
    model.set_initial_status(cfg)

    # Simulation execution
    iterations = model.iteration_bunch(200)



.. [#] J.L. Aron and I.B. Schwartz. Seasonality and period-doubling bifurcations in an epidemic model. Journal Theoretical Biology, 110:665-679, 1984
