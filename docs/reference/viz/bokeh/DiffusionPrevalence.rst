********************
Diffusion Prevalence
********************


The Diffusion Prevalence plot compares the delta-trends of all the statuses allowed by the diffusive model tested.

Each trend line describes the delta of the number of nodes for a given status iteration after iteration. 

.. autoclass:: ndlib.viz.bokeh.DiffusionPrevalence.DiffusionPrevalence
.. automethod:: ndlib.viz.bokeh.DiffusionPrevalence.DiffusionPrevalence.__init__(model, iterations)
.. automethod:: ndlib.viz.bokeh.DiffusionPrevalence.DiffusionPrevalence.plot(width, height)


Below is shown an example of Diffusion Prevalence description and visualization for the SIR model.

.. code-block:: python
    :linenos:

    import networkx as nx
    from bokeh.io import show    import ndlib.models.ModelConfig as mc    import ndlib.models.epidemics.SIRModel as sir 
    from ndlib.viz.bokeh.DiffusionPrevalence import DiffusionPrevalence    # Network topology    g = nx.erdos_renyi_graph(1000, 0.1)
    # Model selection    model = sir.SIRModel(g)    # Model Configuration    cfg = mc.Configuration()    cfg.add_model_parameter('beta', 0.001)    cfg.add_model_parameter('gamma', 0.01)    cfg.add_model_parameter("percentage_infected", 16 0.05)    model.set_initial_status(cfg)    # Simulation execution    iterations = model.iteration_bunch(200)

    # Visualization    viz = DiffusionPrevalence(model, iterations)    p = viz.plot(width=400, height=400)    show(p)



.. figure:: diff_prevalence.png
   :scale: 80 %
   :align: center 
   :alt: SIR Diffusion Prevalence Example

   SIR Diffusion Prevalence Example.