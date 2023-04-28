*********************
General Threshold
*********************

The General Threshold model was introduced in 20003 by Kempe [#]_.

In this model, during an epidemics, a is allowed to change its status from **Susceptible** to **Infected**.

The model is instantiated on a graph having a non-empty set of infected nodes.

The model is defined as follows:

At time *t* nodes become Infected if the sum of the weight of the infected neighbors is greater than the threshold

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
weight     Edge   float in [0, 1]   0.1      False     Edge weight
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
    model = epd.GeneralThresholdModel(g)

    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter('fraction_infected', 0.1)

    # Setting node and edges parameters
    threshold = 0.25
    weight = 0.2
    if isinstance(g, nx.Graph):
        nodes = g.nodes
        edges = g.edges
    else:
        nodes = g.vs['name']
        edges = [(g.vs[e.tuple[0]]['name'], g.vs[e.tuple[1]]['name']) for e in g.es]


    for i in nodes:
        config.add_node_configuration("threshold", i, threshold)
    for e in edges:
        config.add_edge_configuration("weight", e, weight)


    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)



.. [#] János Török and János Kertész “Cascading collapse of online social networks” Scientific reports, vol. 7 no. 1, 2017
    David Kempe , Jon Kleinberg, and Éva Tardos. "Maximizing the spread of influence through a social network." Proceedings of the ninth ACM SIGKDD international conference on Knowledge discovery and data mining. ACM, 2003.
