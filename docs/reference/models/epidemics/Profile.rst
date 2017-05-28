*******
Profile
*******

The Profile model assumes that the diffusion process is only apparent; each node decides to adopt or not a given behavior – once known its existence – only on the basis of its own interests. 

In this scenario the peer pressure is completely ruled out from the overall model: it is not important how many of its neighbors have adopted a specific behaviour, if the node does not like it, it will not change its interests. 

Each node has its own profile describing how many it is likely to accept a behaviour similar to the one that is currently spreading. 

The diffusion process starts from a set of nodes that have already adopted a given behaviour S:

-  for each of the susceptible nodes' in the neighborhood of a node u in S an unbalanced coin is flipped, the unbalance given by the personal profile of the susceptible node;
- if a positive result is obtained the susceptible node will adopt the behaviour, thus becoming infected.

.. autoclass:: ndlib.models.epidemics.ProfileModel.ProfileModel
.. automethod:: ndlib.models.epidemics.ProfileModel.ProfileModel.__init__(graph)

-------
Example
-------

In the code below is shown an example of istantiation and execution of a Profile model simultion on a random graph: we set the initial infected node set to the 10% of the overall population and assign a profile of 0.25 to all the nodes.

.. code-block:: python
    :linenos:

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics.ProfileModel as pr

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = pr.ProfileModel(g)
    config = mc.Configuration()
    config.add_model_parameter('percentage_infected', 0.1)

    # Setting nodes parameters
    profile = 0.15
    for i in g.nodes():
        config.add_node_configuration("profile", i, profile)

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)