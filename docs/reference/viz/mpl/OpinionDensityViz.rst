***************
Opinion Density
***************

The Opinion Density plot shows a 2D density heatmap of opinions over time to prevent spaghetti plot clutter on large networks.

.. autoclass:: ndlib.viz.mpl.OpinionDensityViz.OpinionDensityViz
.. automethod:: ndlib.viz.mpl.OpinionDensityViz.OpinionDensityViz.__init__(model, trends, bins=50)
.. automethod:: ndlib.viz.mpl.OpinionDensityViz.OpinionDensityViz.plot(filename)

Below is shown an example of Opinion Density description and visualization for the Hegselmann-Krause model.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as op
    from ndlib.viz.mpl.OpinionDensityViz import OpinionDensityViz

    g = nx.complete_graph(100)
    model = op.HKModel(g)

    config = mc.Configuration()
    config.add_model_parameter("epsilon", 0.2)
    model.set_initial_status(config)

    iterations = model.iteration_bunch(100)

    viz = OpinionDensityViz(model, iterations)
    viz.plot("opinion_density.pdf")
