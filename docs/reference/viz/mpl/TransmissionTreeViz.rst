*****************
Transmission Tree
*****************

The Transmission Tree plot reconstructs the tree of infection events (who infected whom) and visualizes the secondary infections out-degree distribution (identifying super-spreaders).

.. autoclass:: ndlib.viz.mpl.TransmissionTreeViz.TransmissionTreeViz
.. automethod:: ndlib.viz.mpl.TransmissionTreeViz.TransmissionTreeViz.__init__(model, iterations, active_statuses=["Infected"], susceptible_status="Susceptible")
.. automethod:: ndlib.viz.mpl.TransmissionTreeViz.TransmissionTreeViz.plot(filename)

Below is shown an example of Transmission Tree description and visualization for the SIR model.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as epd
    from ndlib.viz.mpl.TransmissionTreeViz import TransmissionTreeViz

    g = nx.erdos_renyi_graph(1000, 0.1)
    model = epd.SIRModel(g)

    config = mc.Configuration()
    config.add_model_parameter("beta", 0.05)
    config.add_model_parameter("gamma", 0.02)
    config.add_model_parameter("fraction_infected", 0.05)
    model.set_initial_status(config)

    iterations = model.iteration_bunch(100)

    viz = TransmissionTreeViz(model, iterations)
    viz.plot("transmission_tree.pdf")
