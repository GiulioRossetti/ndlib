*****************************
Weighted Hegselmann-Krause
*****************************

The Weighted Hegselmann-Krause was introduced by Toccaceli et al. in 2020 [#]_.

This model is a variation of the well-known Hegselmann-Krause (HK).
Conversely from the HK model, during each iteration WHK consider a random pair-wise interaction involving agents at distance :math:`\epsilon`.
Moreover, to account for the heterogeneity of interaction frequency among agent pairs, WHK leverages edge weights, thus capturing the effect of different social bonds' strength/trust as it happens in reality.
To such extent, each edge :math:`(i,j) \in E`, carries a value :math:`w_{i,j}\in [0,1]`.
The update rule then becomes:

.. math::

        x_i(t+1)= \left\{ \begin{array}{ll}
              x_i(t) + \frac{x_i(t) + x_j(t)w_{i,j}}{2} (1-x_i(t)) &  \quad \quad \mbox{if }  x_i(t) \geq 0\\
              x_i(t) + \frac{x_i(t) + x_j(t)w_{i,j}}{2} (1+x_i(t)) &  \quad \quad \mbox{if } x_i(t) < 0
                \end{array}
                \right.


The idea behind the WHK formulation is that the opinion of agent :math:`i` at time :math:`t+1`, will be given by the combined effect of his previous belief and the average opinion weighed by its, selected, :math:`\epsilon`-neighbor, where :math:`w_{i,j}` accounts for  :math:`i`'s perceived influence/trust of :math:`j`.

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

.. autoclass:: ndlib.models.opinions.WHKModel.WHKModel
.. automethod:: ndlib.models.opinions.WHKModel.WHKModel.__init__(graph)

.. automethod:: ndlib.models.opinions.WHKModel.WHKModel.set_initial_status(self, configuration)
.. automethod:: ndlib.models.opinions.WHKModel.WHKModel.reset(self)

^^^^^^^^
Describe
^^^^^^^^

.. automethod:: ndlib.models.opinions.WHKModel.WHKModel.get_info(self)
.. automethod:: ndlib.models.opinions.WHKModel.WHKModel.get_status_map(self)

^^^^^^^^^^^^^^^^^^
Execute Simulation
^^^^^^^^^^^^^^^^^^
.. automethod:: ndlib.models.opinions.WHKModel.WHKModel.iteration(self)
.. automethod:: ndlib.models.opinions.WHKModel.WHKModel.iteration_bunch(self, bunch_size)

-------
Example
-------

In the code below is shown an example of instantiation and execution of an WHK model simulation on a random graph:
we set the initial set of infected nodes as 1% of the overall population,
assign an epsilon value of 0.32 and a weight equal 0.2 to all the edges.


.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as opn

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = opn.WHKModel(g)

    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter("epsilon", 0.32)

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