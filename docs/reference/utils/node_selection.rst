*******************************
Seed and Immunization Selection
*******************************

``ndlib.node_selection`` ranks nodes so that the initial "Infected" set (seeding) or an initial "Removed" set (immunization) can be chosen by a structural rule instead of at random.

Available strategies: ``random``, ``degree``, ``betweenness``, ``pagerank``, ``kcore`` (coreness, ties broken by degree) and ``collective_influence`` (adaptive, ball radius 2 by default).

The graph is treated as undirected and simple. Ties are broken deterministically.

.. autofunction:: ndlib.node_selection.select_nodes

.. autofunction:: ndlib.node_selection.rank_nodes

-------
Example
-------

**Immunize the 5% of nodes with the highest coreness before an SIR outbreak**

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as ep
    from ndlib.node_selection import select_nodes

    g = nx.barabasi_albert_graph(1000, 3, seed=1)
    immune = select_nodes(g, 50, "kcore")

    model = ep.SIRModel(g, seed=1)
    config = mc.Configuration()
    config.add_model_parameter('beta', 0.05)
    config.add_model_parameter('gamma', 0.2)
    config.add_model_parameter('fraction_infected', 0.01)
    config.add_model_initial_configuration("Removed", immune)
    model.set_initial_status(config)
    iterations = model.iteration_bunch(200)

**Start an independent cascade from the 10 nodes with the highest degree**

.. code-block:: python

    seeds = select_nodes(g, 10, "degree")
    model = ep.IndependentCascadesModel(g, seed=1)
    config = mc.Configuration()
    for e in g.edges():
        config.add_edge_configuration("threshold", e, 0.05)
    config.add_model_initial_configuration("Infected", seeds)
    model.set_initial_status(config)
    iterations = model.iteration_bunch(50)
