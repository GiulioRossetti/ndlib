*****************
Profile Threshold
*****************

The Profile-Threshold model assumes the existence of node profiles that act as preferential schemas for individual tastes but relax the constraints imposed by the Profile model by letting nodes influenceable via peer pressure mechanisms. 

The peer pressure is modeled with a threshold. 

The diffusion process starts from a set of nodes that have already adopted a given behaviour S:

-  for each of the susceptible node an unbalanced coin is flipped if the percentage of its neighbors that are already infected excedes its threhosld. As in the Profile Model the coin unbalance is given by the personal profile of the susceptible node;
- if a positive result is obtained the susceptible node will adopt the behaviour, thus becoming infected. 

.. autoclass:: ndlib.models.epidemics.ProfileThresholdModel.ProfileThresholdModel
.. automethod:: ndlib.models.epidemics.ProfileThresholdModel.ProfileThresholdModel.__init__(graph)

-------
Example
-------

In the code below is shown an example of istantiation and execution of a Profile Threshold model simultion on a random graph: we set the initial infected node set to the 10% of the overall population, assign a profile of 0.25 and a threshold of 0.15 to all the nodes.

.. code-block:: python
    :linenos:

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics.ProfileThresholdModel as pt

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = pt.ProfileThresholdModel(g)
    config = mc.Configuration()
    config.add_model_parameter('percentage_infected', 0.1)

    # Setting nodes parameters
    threshold = 0.15
    profile = 0.25
    for i in g.nodes():
        config.add_node_configuration("threshold", i, threshold)
        config.add_node_configuration("profile", i, profile)
    
    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)
