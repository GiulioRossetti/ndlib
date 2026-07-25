**************
Phase Portrait
**************

The Phase Portrait plot visualizes the trajectory of one model compartment against another over time (e.g., Susceptible vs. Infected).

.. autoclass:: ndlib.viz.mpl.PhasePortraitViz.PhasePortraitViz
.. automethod:: ndlib.viz.mpl.PhasePortraitViz.PhasePortraitViz.__init__(model, trends, status_x="Susceptible", status_y="Infected")
.. automethod:: ndlib.viz.mpl.PhasePortraitViz.PhasePortraitViz.plot(filename)

Below is shown an example of Phase Portrait description and visualization for the SIR model.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as epd
    from ndlib.viz.mpl.PhasePortraitViz import PhasePortraitViz

    g = nx.erdos_renyi_graph(1000, 0.1)
    model = epd.SIRModel(g)

    config = mc.Configuration()
    config.add_model_parameter("beta", 0.05)
    config.add_model_parameter("gamma", 0.02)
    config.add_model_parameter("fraction_infected", 0.05)
    model.set_initial_status(config)

    iterations = model.iteration_bunch(100)
    trends = model.build_trends(iterations)

    viz = PhasePortraitViz(model, trends)
    viz.plot("phase_portrait.pdf")
