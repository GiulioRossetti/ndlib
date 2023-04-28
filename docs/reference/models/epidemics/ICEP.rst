******************************************************************
Independent Cascades with Community Embeddedness and Permeability
******************************************************************

The Independent Cascades with Community Embeddedness and Permeability model was introduced by Milli and Rossetti in 2020 [#]_.

This model is a combination of ICE and ICP methods.

The ICEP model starts with an initial set of **active** nodes A0; the diffusive process unfolds in discrete steps according to the following randomized rule:

- When node v becomes active in step t, it is given a single chance to activate each currently inactive neighbor u. If v and u belong to the same community, the method acts as the ICE model, otherwise as the ICP model.
- If u has multiple newly activated neighbors, their attempts are sequenced in an arbitrary order.
- If v succeeds, then u will become active in step t + 1; but whether or not v succeeds, it cannot make any further attempts to activate u in subsequent rounds.
- The process runs until no more activations are possible.

--------
Statuses
--------

During the simulation a node can experience the following statuses:

===========  ====
Name         Code
===========  ====
Susceptible  0
Infected     1
Removed      2
===========  ====


----------
Parameters
----------

======================  =====  ===============  =======  =========  ======================
Name                    Type   Value Type       Default  Mandatory  Description
======================  =====  ===============  =======  =========  ======================
Edge threshold          Edge   float in [0, 1]   0.1     False      Edge threshold
Community permeability  Model  float in [0, 1]   0.5     True       Community Permeability
======================  =====  ===============  =======  =========  ======================

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

The two options are mutually exclusive and the latter takes precedence over the former.

-------
Example
-------

In the code below is shown an example of instantiation and execution of an ICEP model simulation on a random graph: we set the initial set of infected nodes as 1% of the overall population, assign a threshold of 0.1 to all the edges and set the community permeability equal 0.3.


.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as ep

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = ep.ICEPModel(g)

    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter('fraction_infected', 0.1)
    config.add_model_parameter('permeability', 0.3)


    # Setting the edge parameters
    threshold = 0.1
    for e in g.edges():
        config.add_edge_configuration("threshold", e, threshold)

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] L. Milli and G. Rossetti. “Barriers or Accelerators? Modeling the two-foldnature of meso-scale network topologies indiffusive phenomena,” 2020