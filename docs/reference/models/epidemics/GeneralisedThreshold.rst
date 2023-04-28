*********************
Generalised Threshold
*********************

The Generalised Threshold model was introduced in 2017 by Török and Kertesz [#]_.

In this model, during an epidemics, a node is allowed to change its status from **Susceptible** to **Infected**.

The model is instantiated on a graph having a non-empty set of infected nodes.

The model is defined as follows:

1. At time *t* nodes become Infected with rate *mu* *t*/*tau*
2. Nodes for which the ratio of the active friends dropped below the threshold are moved to the Infected queue
3. Nodes in the Infected queue become infected with rate *tau*. If this happens check all its friends for threshold

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

=========  =====  ===============  =======  =========  =======================
Name       Type   Value Type       Default  Mandatory  Description
=========  =====  ===============  =======  =========  =======================
threshold  Node   float in [0, 1]   0.1      False     Individual threshold
tau        Model  int                        True      Adoption threshold rate
mu         Model  int                        True      Exogenous timescale
=========  =====  ===============  =======  =========  =======================

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

The two options are mutually exclusive and the latter takes precedence over the former.


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
    model = ep.GeneralisedThresholdModel(g)
        
    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter('fraction_infected', 0.1)
    config.add_model_parameter('tau', 5)
    config.add_model_parameter('mu', 5)

    # Setting node parameters
    threshold = 0.25
    for i in g.nodes():
        config.add_node_configuration("threshold", i, threshold)

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] János Török and János Kertész “Cascading collapse of online social networks” Scientific reports, vol. 7 no. 1, 2017 

