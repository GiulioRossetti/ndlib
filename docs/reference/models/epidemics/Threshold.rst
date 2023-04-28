*********
Threshold
*********

The Threshold model was introduced in 1978 by Granovetter [#]_. 

In this model during an epidemic, a node has two distinct and mutually exclusive behavioral alternatives, e.g., the decision to do or not do something, to participate or not participate in a riot. 

Node's individual decision depends on the percentage of its neighbors that have made the same choice, thus imposing a threshold. 

The model works as follows: 
- each node has its own threshold; 
- during a generic iteration every node is observed: if the percentage of its infected neighbors is greater than its threshold it becomes infected as well.

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
