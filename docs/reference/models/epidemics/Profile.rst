*******
Profile
*******
The Profile model was introduced in 2017 by Milli et al. [#]_.


The Profile model assumes that the diffusion process is only apparent; each node decides to adopt or not a given behavior – once known its existence – only on the basis of its own interests. 

In this scenario the peer pressure is completely ruled out from the overall model: it is not important how many of its neighbors have adopted a specific behaviour, if the node does not like it, it will not change its interests. 

Each node has its own profile describing how likely it is to accept a behaviour similar to the one that is currently spreading.

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


-------
Example
-------

In the code below is shown an example of instantiation and execution of a Profile model simulation on a random graph: we set the initial infected node set to the 10% of the overall population and assign a profile of 0.15 to all the nodes.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as ep

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = ep.ProfileModel(g)
    config = mc.Configuration()
    config.add_model_parameter('blocked', 0)
    config.add_model_parameter('adopter_rate', 0)
    config.add_model_parameter('fraction_infected', 0.1)

    # Setting nodes parameters
    profile = 0.15
    for i in g.nodes():
        config.add_node_configuration("profile", i, profile)

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)
    
.. [#] Letizia Milli, Giulio Rossetti, Dino Pedreschi, Fosca Giannotti, “Information Diffusion in Complex Networks: The Active/Passive Conundrum,” Proceedings of International Conference on Complex Networks and their Applications, (pp. 305-313). Springer, Cham. 2017
