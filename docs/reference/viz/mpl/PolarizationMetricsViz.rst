********************
Polarization Metrics
********************

The Polarization Metrics plot tracks quantitative opinion metrics (entropy, standard deviation, and mean pairwise absolute difference) over time.

.. autoclass:: ndlib.viz.mpl.PolarizationMetricsViz.PolarizationMetricsViz
.. automethod:: ndlib.viz.mpl.PolarizationMetricsViz.PolarizationMetricsViz.__init__(model, trends)
.. automethod:: ndlib.viz.mpl.PolarizationMetricsViz.PolarizationMetricsViz.plot(filename)

Below is shown an example of Polarization Metrics description and visualization for the Hegselmann-Krause model.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as op
    from ndlib.viz.mpl.PolarizationMetricsViz import PolarizationMetricsViz

    g = nx.complete_graph(100)
    model = op.HKModel(g)

    config = mc.Configuration()
    config.add_model_parameter("epsilon", 0.2)
    model.set_initial_status(config)

    iterations = model.iteration_bunch(100)

    viz = PolarizationMetricsViz(model, iterations)
    viz.plot("polarization_metrics.pdf")
