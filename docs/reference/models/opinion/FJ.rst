****************
Friedkin-Johnsen
****************

The Friedkin-Johnsen (FJ) model is a continuous opinion dynamics model originally introduced by Noah E. Friedkin and Eugene C. Johnsen [#]_.

The model extends the classical DeGroot consensus model by introducing stubbornness. At each iteration, agents update their opinions by taking a weighted average of their neighbors' opinions, but they also retain a persistent attachment (stubbornness) to their initial opinion:

.. math::

    x_i(t+1) = (1 - \theta_i) \sum_{j} W_{ij} x_j(t) + \theta_i x_i(0)

where :math:`\theta_i` is the node stubbornness parameter and :math:`x_i(0)` is the initial opinion of node :math:`i`.

--------
Statuses
--------

During the simulation, a node can experience the following statuses:

=========  ====
Name       Code
=========  ====
Infected   0
=========  ====

Note: The opinion is represented as a continuous value (typically in [0, 1] or [-1, 1]) corresponding to the Infected status.

----------
Parameters
----------

    - **init_dist_lower**: Model Parameter, float, lower bound of initial opinion distribution. Default 0.
    - **init_dist_upper**: Model Parameter, float, upper bound of initial opinion distribution. Default 1.
    - **stubbornness**: Node Parameter, float in [0, 1], level of stubbornness. Default 0.1.

-------
Example
-------

In the code below, we show an example of instantiation and execution of a Friedkin-Johnsen model simulation on a random graph:

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as op

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = op.FJModel(g)
    config = mc.Configuration()
    config.add_model_parameter('init_dist_lower', -0.5)
    config.add_model_parameter('init_dist_upper', 0.5)

    # Add stubbornness parameter for nodes
    for node in g.nodes():
        config.add_node_configuration('stubbornness', node, 0.2)

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(10)


.. [#] N. E. Friedkin and E. C. Johnsen, “Social influence and opinions,” Journal of Mathematical Sociology, vol. 15, no. 3-4, pp. 193–206, 1990.
