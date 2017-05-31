************************
Describe a Visuzlization
************************

All the bokeh visualizations implemented so far in ``NDlib`` extends the abstract class ``nndlib.viz.bokeh.DiffusionViz.DiffusionPlot``.

.. autoclass:: ndlib.viz.bokeh.DiffusionViz.DiffusionPlot

So far ``DiffusionPlot`` implements the visualization logic *only* for generic **trend line plot** built upon simulation iterations and model metadata.

--------------------
Line Plot Definition
--------------------

As convention a new visualization should be described in a python file named after it, e.g. a ``MyViz`` class should be implemented in a ``MyViz.py`` file.

.. automethod:: ndlib.viz.bokeh.DiffusionViz.DiffusionPlot.__init__(self, model, iteration)


In oder to effectively describe the visualization the ``__init__`` function of ``ndlib.viz.bokeh.DiffusionViz.DiffusionPlot`` must be specified as follows:

.. code-block:: python

	from ndlib.viz.bokeh.DiffusionViz import DiffusionPlot

	class MyViz(DiffusionPlot):

		def __init__(self, model, iterations):
			super(self.__class__, self).__init__(model, iterations)
			self.ylabel = "Y label"
			self.xlabel = "X label"
			self.title = "Plot Title"


----------------
Data Preparation
----------------

Once described the plot metadata it is necessary to prepare the data to be visualized through the ``plot()`` method.

To do so, the ``iteration_series()`` method of the base class has to be overridden in ``MyViz``.

.. automethod:: ndlib.viz.bokeh.DiffusionViz.DiffusionPlot.iteration_series(self)

Such method can access the iterations data, as returned by ``ndlib.models.DiffusionModel.DiffusionModel.iteration_bunch(self, bunch_size)`` in ``self.iterations``.

