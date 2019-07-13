********
Tutorial
********

NDlib is built upon networkx and is designed to configure, simulate and visualize diffusion experiments.

Here you can find a few examples to get started with ``ndlib``: for a more comprehensive tutorial check the official `Jupyter Notebook`_.

------------
Installation
------------

In order to install the latest version of the library (with visualization facilities) use

.. code:: bash

    pip install ndlib

-----------------------
Chose a Diffusion model
-----------------------

Let's start importing the required libraries

.. code:: python

    import networkx as nx
    import ndlib.models.epidemics as ep

Once imported the epidemic model module and the networkx library we can initialize the simulation:

.. code:: python

    # Network Definition
    g = nx.erdos_renyi_graph(1000, 0.1)
    
    # Model Selection
    model = ep.SIRModel(g)

------------------------
Configure the simulation
------------------------

Each model has its own parameters: in order to completely instantiate the simulation we need to specify them using a ``Configuration`` object:

.. code:: python

    import ndlib.models.ModelConfig as mc

    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter('beta', 0.001)
    config.add_model_parameter('gamma', 0.01)
    config.add_model_parameter("fraction_infected", 0.05)
    model.set_initial_status(config)

The model configuration allows to specify model parameters (as in this scenario) as well as nodes' and edges' ones (e.g.  individual thresholds).

Moreover it allows to specify the initial fraction of infected nodes using the 
``fraction_infected`` model parameter.

It is also possible to explicitly specify an initial set of infected nodes: see :ref:`model_conf` for the complete set of use cases.

----------------------
Execute the simulation
----------------------

In order to execute the simulation one, or more, iterations must be required using the ``model.iteration()`` and/or ``model.iteration_bunch(n_iterations)`` methods.

.. code:: python

	# Simulation
	iterations = model.iteration_bunch(200)
	trends = model.build_trends(iterations)

---------------------
Visualize the results
---------------------

At the end of the simulation the diffusion trend can be visualized as follows (for ``matplotlib`` change ``ndlib.viz.bokeh`` in ``ndlib.viz.mpl``)

.. code:: python

	from bokeh.io import output_notebook, show
	from ndlib.viz.bokeh.DiffusionTrend import DiffusionTrend

	viz = DiffusionTrend(model, trends)
	p = viz.plot(width=400, height=400)
	show(p)

Furthermore, a prevalence plot is also made available.

The prevalence plot captures the variation (delta) of nodes for each status in consecutive iterations.

.. code:: python

	from ndlib.viz.bokeh.DiffusionPrevalence import DiffusionPrevalence

	viz2 = DiffusionPrevalence(model, trends)
	p2 = viz2.plot(width=400, height=400)
	show(p2)


Multiple plots can be combined in a multiplot to provide a complete description of the diffusive process

.. code:: python

	from ndlib.viz.bokeh.MultiPlot import MultiPlot
	vm = MultiPlot()
	vm.add_plot(p)
	vm.add_plot(p2)
	m = vm.plot()
	show(m)


Multiplots - implemented only for the ``bokeh`` provider - are also useful to compare different diffusion models applied to the same graph (as well as a same model instantiated with different parameters)

.. code:: python

	import ndlib.models.epidemics as ep

	vm = MultiPlot()
	vm.add_plot(p)

	# SIS
	sis_model = ep.SISModel(g)
	config = mc.Configuration()
	config.add_model_parameter('beta', 0.001)
	config.add_model_parameter('lambda', 0.01)
	config.add_model_parameter("fraction_infected", 0.05)
	sis_model.set_initial_status(config)
	iterations = sis_model.iteration_bunch(200)
	trends = sis_model.build_trends(iterations)

	viz = DiffusionTrend(sis_model, trends)
	p3 = viz.plot(width=400, height=400)
	vm.add_plot(p3)

	# SI
	si_model = ep.SIModel(g)
	config = mc.Configuration()
	config.add_model_parameter('beta', 0.001)
	config.add_model_parameter("fraction_infected", 0.05)
	si_model.set_initial_status(config)
	iterations = si_model.iteration_bunch(200)
	trends = si_model.build_trends(iterations)

	viz = DiffusionTrend(si_model, trends)
	p4 = viz.plot(width=400, height=400)
	vm.add_plot(p4)

	# Threshold
	th_model = ep.ThresholdModel(g)
	config = mc.Configuration()

	# Set individual node threshold
	threshold = 0.40
	for n in g.nodes():
		config.add_node_configuration("threshold", n, threshold)

	config.add_model_parameter("fraction_infected", 0.30)
	th_model.set_initial_status(config)
	iterations = th_model.iteration_bunch(60)
	trends = th_model.build_trends(iterations)

	viz = DiffusionTrend(th_model, trends)
	p5 = viz.plot(width=400, height=400)
	vm.add_plot(p5)

	m = vm.plot()
	show(m)


.. _`Jupyter Notebook`: https://colab.research.google.com/github/KDDComplexNetworkAnalysis/CNA_Tutorials/blob/master/NDlib.ipynb#scrollTo=d80DUNRkKIn4
