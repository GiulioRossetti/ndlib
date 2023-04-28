
-------
Example
-------

In the code below is shown an example of instantiation and execution of an ARWHK model simulation on a
random graph: we assign an epsilon value of 0.32, the percentage of stubborness equal 0.2, the distribution of stubborness equal 0
and a weight equal 0.2 to all the edges.


.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as opn

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = opn.ARWHKModel(g)

    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter("epsilon", 0.32)
    config.add_model_parameter("perc_stubborness", 0.2)
    config.add_model_parameter("option_for_stubbornness", 0)
    config.add_model_parameter("method_variant", 2)

    # Setting the edge parameters
    weight = 0.2
    if isinstance(g, nx.Graph):
        edges = g.edges
    else:
        edges = [(g.vs[e.tuple[0]]['name'], g.vs[e.tuple[1]]['name']) for e in g.es]

    for e in edges:
        config.add_edge_configuration("weight", e, weight)


    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(20)


.. [#] C. Toccaceli, L. Milli and G. Rossetti. “Opinion Dynamic modeling of Fake News Perception,” in Proceedings of International Conference on Complex Networks and Their Applications, 2020.