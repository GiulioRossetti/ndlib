*********
Threshold
*********

The Threshold model was introduced in 1978 by Granovetter [#]_. 

In this model during an epidemics, a node has two distinct and mutually exclusive behavioral alternatives, e.g., the decision to do or not do something, to participate or not participate in a riot. 

Node's individual decision depends on the percentage of its neighbors have made the same choice, thus imposing a threshold. 

The model works as follows: 
- each node has its own threshold; 
- during a generic iteration every node is observed: iff the percentage of its infected neighbors is grater than its threshold it becomes infected as well.

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

=========  =====  ===============  =======  =========  =====================
Name       Type   Value Type       Default  Mandatory  Description
=========  =====  ===============  =======  =========  =====================
threshold  Node   float in [0, 1]   0.1      False     Individual threshold
=========  =====  ===============  =======  =========  =====================

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
.. autoclass:: ndlib.models.epidemics.ThresholdModel.ThresholdModel
.. automethod:: ndlib.models.epidemics.ThresholdModel.ThresholdModel.__init__(graph)

.. automethod:: ndlib.models.epidemics.ThresholdModel.ThresholdModel.set_initial_status(self, configuration)
.. automethod:: ndlib.models.epidemics.ThresholdModel.ThresholdModel.reset(self)

^^^^^^^^
Describe
^^^^^^^^

.. automethod:: ndlib.models.epidemics.ThresholdModel.ThresholdModel.get_info(self)
.. automethod:: ndlib.models.epidemics.ThresholdModel.ThresholdModel.get_status_map(self)

^^^^^^^^^^^^^^^^^^
Execute Simulation
^^^^^^^^^^^^^^^^^^
.. automethod:: ndlib.models.epidemics.ThresholdModel.ThresholdModel.iteration(self)
.. automethod:: ndlib.models.epidemics.ThresholdModel.ThresholdModel.iteration_bunch(self, bunch_size)


-------
Example
-------

In the code below is shown an example of instantiation and execution of a Threshold model simulation on a random graph: we set the initial set of infected nodes as 1% of the overall population, and assign a threshold of 0.25 to all the nodes.


.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as ep

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = ep.ThresholdModel(g)
        
    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter('fraction_infected', 0.1)

    # Setting node parameters
    threshold = 0.25
    for i in g.nodes():
        config.add_node_configuration("threshold", i, threshold)

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] M. Granovetter, “Threshold models of collective behavior,” The American Journal of Sociology, vol. 83, no. 6, pp. 1420–1443, 1978.
