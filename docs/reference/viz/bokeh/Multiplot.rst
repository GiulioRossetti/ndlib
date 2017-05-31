**********
Multi Plot
**********

The Multi Plot object allows the generation of composite grid figures composed by multiple Diffusion Trends and/or Diffusion Prevalence plots.


.. autoclass:: ndlib.viz.bokeh.MultiPlot.MultiPlot
.. automethod:: ndlib.viz.bokeh.MultiPlot.MultiPlot.add_plot(plot)
.. automethod:: ndlib.viz.bokeh.MultiPlot.MultiPlot.plot(width, height)

.. code-block:: python

    import networkx as nx
    from bokeh.io import show
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics.SIRModel as sir 
    from ndlib.viz.bokeh.DiffusionTrend import DiffusionTrend
    from ndlib.viz.bokeh.DiffusionPrevalence import DiffusionPrevalence
    from ndlib.viz.bokeh.MultiPlot import Multiplot

    vm = MultiPlot()

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = sir.SIRModel(g)

    # Model Configuration
    cfg = mc.Configuration()
    cfg.add_model_parameter('beta', 0.001)
    cfg.add_model_parameter('gamma', 0.01)
    cfg.add_model_parameter("percentage_infected", 16 0.05)
    model.set_initial_status(cfg)

    # Simulation execution
    iterations = model.iteration_bunch(200)

    # Diffusion Trend
    viz = DiffusionTrend(model, iterations)
    p = viz.plot(width=400, height=400)
    vm.add_plot(p)

    # Diffusion Prevalence
    viz = DiffusionPrevalence(model, iterations)
    p1 = viz.plot(width=400, height=400)
    
    vm.add_plot(p1)
    
    m = vm.plot(ncol=2)
    show(m)
