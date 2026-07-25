************
Peak Metrics
************

The Peak Metrics plot aggregates simulation data across multiple runs to show boxplots of the Peak Infected Fraction and the Outbreak Duration.

.. autoclass:: ndlib.viz.mpl.PeakMetricsViz.PeakMetricsViz
.. automethod:: ndlib.viz.mpl.PeakMetricsViz.PeakMetricsViz.__init__(model, trends, status_infected="Infected")
.. automethod:: ndlib.viz.mpl.PeakMetricsViz.PeakMetricsViz.plot(filename)

Below is shown an example of Peak Metrics description and visualization for the SIR model.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as epd
    from ndlib.viz.mpl.PeakMetricsViz import PeakMetricsViz

    g = nx.erdos_renyi_graph(1000, 0.1)
    model = epd.SIRModel(g)

    config = mc.Configuration()
    config.add_model_parameter("beta", 0.05)
    config.add_model_parameter("gamma", 0.02)
    config.add_model_parameter("fraction_infected", 0.05)
    model.set_initial_status(config)

    # Execute multiple simulation runs to collect trends
    trends_list = []
    for i in range(10):
        model.reset()
        iterations = model.iteration_bunch(100)
        trends = model.build_trends(iterations)
        trends_list.append(trends[0])

    viz = PeakMetricsViz(model, trends_list)
    viz.plot("peak_metrics.pdf")
