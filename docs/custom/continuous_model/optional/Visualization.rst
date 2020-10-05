******************************
Continuous Model Visualization
******************************

Visualization is often a very important section. The continuous model class allows for a lot of flexibility for what should be shown.
In general, the usual functions like creatings trends, and normally plotting work in the same manner as for the ``CompositeModel``.
But more features have been added to also visualize the specified network and color the nodes using an internal state.
The other states are shown beneath the network graph using histogram figures.

-------
Example
-------

This is an example generated visualization. It shows addiction as a node color, while the other states of the model are shown using histograms.

.. figure:: https://i.imgur.com/pZBmhc3.gif
   :align: center
   :alt: Continuous Visualization

-------------
Configuration
-------------

To configure and enable visualization, a configuration dictionary should be created first.

It should hold the following key -> value mappings:

==================  ===============  =====================================  =========  =================================================================
Key (string)        Value Type       Default                                Mandatory  Description
==================  ===============  =====================================  =========  =================================================================
plot_interval       number                                                  True       How many iterations should be between each plot
plot_variable       string                                                  True       The state to use as node color
show_plot           boolean          True                                   False      Whether a plot should be shown
plot_output         string                                                  False      Should be a path + file name, if set it will save a gif there
plot_title          string           Network simulation of `plot_variable`  False      The title of the visualization
plot_annotation     string                                                  False      The annotation of the visualization
cmin                number           0                                      False      The minimum color to display in the colorbar
cmax                number           0                                      False      The maximum color to display in the colorbar
color_scale         string           RdBu                                   False      Matplotlib colorscale colors to use
layout              string|function  nx.drawing.spring_layout               False      Name of the networkx layout to use
layout_params       dictionary                                              False      Arguments to pass to layout function, takes argument name as key
variable_limits     dictionary       {state: [-1, 1] for state in states}   False      Dictionary mapping state name to a list with min and max value
animation_interval  integer          30                                     False      Amount of miliseconds between each frame
==================  ===============  =====================================  =========  =================================================================

When the configuration dictionary has been initialized and the model has been initialized, it can be added to the model using the function ``configure_visualization(visualization_dictionary)``.

.. note::

    By default, if the nodes in the networkx graph already have positions (the pos attribute is set per node), 
    then the positions of the nodes will be used as a layout. If no positions are set, a spring layout will be used, or a specified layout will be used.

    The ``layout`` key currently supports some igraph layouts as well, but it requires the igraph and pyintergraph libraries installed.

    The following igraph layouts are supported:

	- ``fr``: Creates an igraph layout using the fruchterman reingold algorithm

    It is possible to include any function, that takes the graph as argument and returns a dictionary of positions keyed by node, 
    just like how the networkx.drawing._layout functions work. This means all networkx layout functions can be included as layout value.

    If you wish to pass any specific arguments to the function included as layout, this can be done using the layout_params key. 
    Simply map it to a dict that has the parameter name as key and the desired value as value.


Example:

.. code-block:: python

    import networkx as nx
    from ndlib.models.ContinuousModel import ContinuousModel

    g = nx.erdos_renyi_graph(n=1000, p=0.1)

    model = ContinuousModel(g)
    model.add_status('status_1')

    # Visualization config
    visualization_config = {
        'plot_interval': 5,
        'plot_variable': 'status_1',
        'variable_limits': {
            'status_1': [0, 0.8]
        },
        'show_plot': True,
        'plot_output': './animations/model_animation.gif',
        'plot_title': 'Animated network',
    }

    model.configure_visualization(visualization_config)

After running the model using the ``iteration_bunch`` function, the returned value can then be used to call the ``visualize(iterations)`` function, which will produce the plot shown in animation above.

It is also possible to recreate the standard static plots using the ``plot(trends, len(iterations), delta=True)`` function. The first argument takes the trends created by the ``build_trends(iterations)`` function.