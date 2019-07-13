********************
Diffusion Prevalence
********************


The Diffusion Prevalence plot compares the delta-trends of all the statuses allowed by the diffusive model tested.

Each trend line describes the delta of the number of nodes for a given status iteration after iteration. 

.. autoclass:: ndlib.viz.mpl.DiffusionPrevalence.DiffusionPrevalence
.. automethod:: ndlib.viz.mpl.DiffusionPrevalence.DiffusionPrevalence.__init__(model, trends)
.. automethod:: ndlib.viz.mpl.DiffusionPrevalence.DiffusionPrevalence.plot(filename, percentile)


Below is shown an example of Diffusion Prevalence description and visualization for the SIR model.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as ep
    from ndlib.viz.mpl.DiffusionPrevalence import DiffusionPrevalence


    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = ep.SIRModel(g)

    # Model Configuration
    cfg = mc.Configuration()
    cfg.add_model_parameter('beta', 0.001)
    cfg.add_model_parameter('gamma', 0.01)
    cfg.add_model_parameter("fraction_infected", 0.01)
    model.set_initial_status(cfg)

    # Simulation execution
    iterations = model.iteration_bunch(200)
    trends = model.build_trends(iterations)

    # Visualization
    viz = DiffusionPrevalence(model, trends)
    viz.plot("prevalence.pdf")



.. figure:: diff_prevalence.png
   :scale: 80 %
   :align: center 
   :alt: SIR Diffusion Prevalence Example

   SIR Diffusion Prevalence Example.
