********************
Diffusion Animator
********************

The Diffusion Animator visualises a diffusion process as a frame-by-frame
animation of the network graph.  Node colours reflect the simulated status at
each iteration: a categorical palette is used for discrete-state models
(e.g. SIR) and a sequential colourmap (``RdYlBu_r``) for continuous-opinion
models.

.. autoclass:: ndlib.viz.mpl.DiffusionAnimator.DiffusionAnimator
.. automethod:: ndlib.viz.mpl.DiffusionAnimator.DiffusionAnimator.__init__(model, iterations, pos)
.. automethod:: ndlib.viz.mpl.DiffusionAnimator.DiffusionAnimator.plot()
.. automethod:: ndlib.viz.mpl.DiffusionAnimator.DiffusionAnimator.save_gif(filename, fps)


Below is a minimal example for the SIR model.

.. code-block:: python

    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as epd
    from ndlib.viz.mpl.DiffusionAnimator import DiffusionAnimator
    import networkx as nx

    # Network topology
    g = nx.erdos_renyi_graph(20, 0.2)

    # Model selection
    model = epd.SIRModel(g)

    # Model configuration
    cfg = mc.Configuration()
    cfg.add_model_parameter('beta', 0.5)
    cfg.add_model_parameter('gamma', 0.1)
    cfg.add_model_parameter("fraction_infected", 0.2)
    model.set_initial_status(cfg)

    # Simulation execution
    iterations = model.iteration_bunch(20)

    # Animation – returns matplotlib.animation.FuncAnimation
    viz = DiffusionAnimator(model, iterations)
    anim = viz.plot()                  # display inline in Jupyter, or …
    viz.save_gif("sir.gif", fps=3)     # … export as a GIF
