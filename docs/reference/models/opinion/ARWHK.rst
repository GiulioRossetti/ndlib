************************************************
Attraction-Repulsion Weighted Hegselmann-Krause
************************************************

The Attraction-Repulsion Weighted Hegselmann-Krause was introduced by Toccaceli et al. in 2020 [#]_.

This model is a variation of the Weighted Hegselmann-Krause (WHK).
This model considers pair-wise interactions.
To model the attraction and repulsion of opinions, during each iteration an agent :math:`i` is randomly
selected along with one of its neighbors, :math:`j` - not taking into account the :math:`\epsilon` threshold.
Once identified the pair-wise interaction, the absolute value of the difference between the opinions of :math:`i`
and :math:`j` is computed.
There are four different variants of the method:

1. Base case: If the computed difference value is lower than :math:`\epsilon` then the update rule becomes:

.. math::

        x_i(t+1)= \left\{ \begin{array}{ll}
              x_i(t) + \frac{x_i(t) + x_j(t)w_{i,j}}{2} (1-x_i(t)) &  \quad \quad \mbox{if }  x_i(t) \geq 0\\
              x_i(t) + \frac{x_i(t) + x_j(t)w_{i,j}}{2} (1+x_i(t)) &  \quad \quad \mbox{if } x_i(t) < 0
                \end{array}
                \right.

2. Attraction: if the computed difference value is lower than :math:`\epsilon` then the following update rule are applied:

.. math::

        x_i(t+1)=\begin{cases}
            x_i(t) - \frac{sum_{op}}{2} (1-x_i(t)) & \text{if x_i(t) \geq 0,  x_j(t) \geq 0, x_i(t) > x_j(t) }\\
            x_i(t) + \frac{sum_{op}}{2} (1-x_i(t)) & \text{if x_i(t) \geq 0,  x_j(t) \geq 0, x_i(t) < x_j(t) } \\
            x_i(t) + \frac{sum_{op}}{2} (1+x_i(t)) & \text{if x_i(t) < 0,  x_j(t) < 0, x_i(t) > x_j(t) }\\
            x_i(t) - \frac{sum_{op}}{2} (1+x_i(t)) & \text{if x_i(t) < 0,  x_j(t) < 0, x_i(t) < x_j(t) } \\
            x_i(t) - \frac{sum_{op}}{2} (1-x_i(t)) & \text{if x_i(t) \geq 0,  x_j(t) < 0, sum_{op} > 0}\\
            x_i(t) + \frac{sum,_{op}}{2} (1-x_i(t)) & \text{if x_i(t) \geq 0,  x_j(t) < 0, sum_{op} < 0}\\
            x_i(t) + \frac{sum_{op}}{2} (1+x_i(t)) & \text{if x_i(t) < 0,  x_j(t) \geq 0, sum_{op} > 0}\\
            x_i(t) - \frac{sum_{op}}{2} (1+x_i(t)) & \text{if x_i(t) < 0,  x_j(t) \geq 0, sum_{op} < 0}\\
            \end{cases}

where :math:`sum_{op} = x_i(t) + x_j(t)w_{i,j}`.

3. Repulsion: if the difference between :math:`x_i(t)` and :math:`x_j(t)` exceeds :math:`\epsilon` then the following update rule are applied:

.. math::
        x_i(t+1)=\begin{cases}
             x_i(t) + \frac{sum{op}}{2} (1-x_i(t)) & \text{if x_i(t) \geq 0,  x_j(t) \geq 0, x_i(t) > x_j(t) }\\
             x_i(t) - \frac{sum_{op}}{2} (1-x_i(t)) & \text{if x_i(t) \geq 0,  x_j(t) \geq 0, x_i(t) < x_j(t)} \\
             x_i(t) - \frac{sum_{op}}{2} (1+x_i(t)) & \text{if x_i(t) < 0,  x_j(t) < 0, x_i(t) > x_j(t) }\\
             x_i(t) + \frac{sum_{op}}{2} (1+x_i(t)) & \text{if x_i(t) < 0,  x_j(t) < 0, x_i(t) < x_j(t) } \\
             x_i(t) + \frac{sum_{op}}{2} (1-x_i(t)) & \text{if x_i(t) \geq 0,  x_j(t) < 0, sum_{op} > 0}\\
             x_i(t) - \frac{sum_{op}}{2} (1-x_i(t)) & \text{if x_i(t) \geq 0,  x_j(t) < 0, sum_{op} < 0}\\
             x_i(t) - \frac{sum_{op}}{2} (1+x_i(t)) & \text{if x_i(t) < 0,  x_j(t) \geq 0, sum_{op} > 0}\\
             x_i(t) + \frac{sum_{op}}{2} (1+x_i(t)) & \text{if x_i(t) < 0,  x_j(t) \geq 0, sum_{op} < 0}\\
            \end{cases}

where :math:`sum_{op} = x_i(t) + x_j(t)w_{i,j}`.

4. Attraction and Repulsion: if the computed difference value is lower than :math:`\epsilon` then the attraction interaction occurs,
otherwise the repulsion attraction occurs.

--------
Statuses
--------

Node statuses are continuous values in [-1,1].

----------
Parameters
----------

===========================  =====  =========================  =======  =========  ==============================================
Name                         Type   Value Type                 Default  Mandatory  Description
===========================  =====  =========================  =======  =========  ==============================================
epsilon                      Model  float in [0, 1]             ---     True       Bounded confidence threshold
perc_stubborness             Model  float in [0, 1]             0       False      Percentage of stubborn agent
similarity                   Model  int in {0, 1}               0       False      The method use the feature of the nodes ot not
option_for_stubbornness      Model  int in {-1,0, 1}            0       False      Define distribution of stubborns
method_variant               Model  int in {0, 1, 2, 3}         0       False      The choice of the method to apply
weight                       Edge   float in [0, 1]             0.1     False      Edge weight
stubborn                     Node   int in {0, 1}               0       False      The agent is stubborn or not
vector                       Node   Vector of float in [0, 1]   []      False      Vector represents the character of the node
===========================  =====  =========================  =======  =========  ==============================================

-------
Methods
-------

The following class methods are made available to configure, describe and execute the simulation:


^^^^^^^^^
Configure
^^^^^^^^^

.. autoclass:: ndlib.models.opinions.ARWHKModel.ARWHKModel
.. automethod:: ndlib.models.opinions.ARWHKModel.ARWHKModel.__init__(graph)

.. automethod:: ndlib.models.opinions.ARWHKModel.ARWHKModel.set_initial_status(self, configuration)
.. automethod:: ndlib.models.opinions.ARWHKModel.ARWHKModel.reset(self)

^^^^^^^^
Describe
^^^^^^^^

.. automethod:: ndlib.models.opinions.ARWHKModel.ARWHKModel.get_info(self)
.. automethod:: ndlib.models.opinions.ARWHKModel.ARWHKModel.get_status_map(self)

^^^^^^^^^^^^^^^^^^
Execute Simulation
^^^^^^^^^^^^^^^^^^
.. automethod:: ndlib.models.opinions.ARWHKModel.ARWHKModel.iteration(self)
.. automethod:: ndlib.models.opinions.ARWHKModel.ARWHKModel.iteration_bunch(self, bunch_size)


-------
Example
-------

In the code below is shown an example of instantiation and execution of an ARWHK model simulation on a
random graph: we assign an epsilon value of 0.32, the percentage of stubborness equal 0.2, the distribution of stubborness equal 0
and a weight equal 0.2 to all the edges.


.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as opn

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = opn.ARWHKModel(g)

    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter("epsilon", 0.32)
    config.add_model_parameter("perc_stubborness", 0.2)
    config.add_model_parameter("option_for_stubbornness", 0)
    config.add_model_parameter("method_variant", 2)

    # Setting the edge parameters
    weight = 0.2
    if isinstance(g, nx.Graph):
        edges = g.edges
    else:
        edges = [(g.vs[e.tuple[0]]['name'], g.vs[e.tuple[1]]['name']) for e in g.es]

    for e in edges:
        config.add_edge_configuration("weight", e, weight)


    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(20)


.. [#] C. Toccaceli, L. Milli and G. Rossetti. “Opinion Dynamic modeling of Fake News Perception,” in Proceedings of International Conference on Complex Networks and Their Applications, 2020.