*******
Profile
*******

The Profile model, introduced by Milli et al. in [#]_, assumes that the diffusion process is only apparent; each node decides to adopt or not a given behavior – once known its existence – only on the basis of its own interests.

In this scenario the peer pressure is completely ruled out from the overall model: it is not important how many of its neighbors have adopted a specific behaviour, if the node does not like it, it will not change its interests. 

Each node has its own profile describing how many it is likely to accept a behaviour similar to the one that is currently spreading. 

The diffusion process starts from a set of nodes that have already adopted a given behaviour S:

- for each of the susceptible nodes' in the neighborhood of a node u in S an unbalanced coin is flipped, the unbalance given by the personal profile of the susceptible node;
- if a positive result is obtained the susceptible node will adopt the behaviour, thus becoming infected.
- if the **blocked** status is enabled, after having rejected the adoption with probability ``blocked`` a node becomes immune to the infection.
- every iteration ``adopter_rate`` percentage of nodes spontaneous became infected to endogenous effects.



--------
Statuses
--------

During the simulation a node can experience the following statuses:

===========  ====
Name         Code
===========  ====
Susceptible  0
Infected     1
Blocked      -1
===========  ====

----------
Parameters
----------

============  =====  ===============  =======  =========  ===================
Name          Type   Value Type       Default  Mandatory  Description
============  =====  ===============  =======  =========  ===================
profile       Node   float in [0, 1]   0.1     False      Node profile
blocked       Model  float in [0, 1]   0       False      Blocked nodes
adopter_rate  Model  float in [0, 1]   0       False      Autonomous adoption
============  =====  ===============  =======  =========  ===================

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

The two options are mutually exclusive and the latter takes precedence over the former.

*NB: the ``execute_iterations()`` method is unavailable for this model (along with other thresholded models).*

-------
Example
-------

In the code below is shown an example of instantiation and execution of a Profile model simulation on a random graph: we set the initial infected node set to the 10% of the overall population and assign a profile of 0.25 to all the nodes.

.. code-block:: python

    import networkx as nx
    import dynetx as dn
    import ndlib.models.ModelConfig as mc
    import ndlib.models.dynamic as dm
    from past.builtins import xrange

    # Dynamic Network topology
    dg = dn.DynGraph()

    for t in xrange(0, 3):
        g = nx.erdos_renyi_graph(200, 0.05)
        dg.add_interactions_from(g.edges(), t)

    # Model selection
    model = dm.DynProfileModel(dg)
    config = mc.Configuration()
    config.add_model_parameter('blocked', 0)
    config.add_model_parameter('adopter_rate', 0)
    config.add_model_parameter('fraction_infected', 0.1)

    # Setting nodes parameters
    profile = 0.15
    for i in g.nodes():
        config.add_node_configuration("profile", i, profile)

    model.set_initial_status(config)


    # Simulate snapshot based execution
    iterations = model.execute_snapshots()

.. [#] Milli, L., Rossetti, G., Pedreschi, D., & Giannotti, F. (2018). Active and passive diffusion processes in complex networks. Applied network science, 3(1), 42.
