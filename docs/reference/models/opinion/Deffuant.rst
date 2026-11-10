********************
Deffuant-Weisbuch
********************

The Deffuant-Weisbuch model was introduced in 2000 by Deffuant, Neau, Amblard, and Weisbuch [#]_.
It is one of the foundational continuous opinion dynamics models with bounded confidence.

In each iteration, :math:`N` pairwise interactions are drawn uniformly at random from the edge set
(where :math:`N` is the number of nodes in the graph). For each selected pair of connected agents
:math:`i` and :math:`j`, they compare their opinions:

.. math::

    |x_i(t) - x_j(t)| \le \epsilon

If their opinion distance is within the confidence threshold :math:`\epsilon`, both agents converge toward
each other weighted by the convergence parameter :math:`\mu`:

.. math::

    x_i(t+1) = x_i(t) + \mu \cdot (x_j(t) - x_i(t))

    x_j(t+1) = x_j(t) + \mu \cdot (x_i(t) - x_j(t))

Otherwise, if :math:`|x_i(t) - x_j(t)| > \epsilon`, no interaction occurs and opinions remain unchanged.
When :math:`\mu = 0.5`, interacting agents take their exact arithmetic mean.
Depending on :math:`\epsilon`, the population either reaches consensus or fragments into multiple stable opinion clusters.

--------
Statuses
--------

Node statuses are continuous values in [0, 1].

----------
Parameters
----------

============================  =====  =========================  =========  =========  ==============================================================
Name                          Type   Value Type                 Default    Mandatory  Description
============================  =====  =========================  =========  =========  ==============================================================
epsilon                       Model  float in [0, 1]            ---        True       Bounded confidence threshold
mu                            Model  float in (0, 0.5]          0.5        False      Convergence / cautiousness parameter
initial_opinion_distribution  Model  string                     "uniform"  False      Initial distribution: uniform, normal, gaussian, bimodal, etc.
============================  =====  =========================  =========  =========  ==============================================================


-------
Example
-------

In the code below is shown an example of instantiation and execution of a Deffuant model simulation on a random graph:

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as opn

    # Network topology
    g = nx.erdos_renyi_graph(100, 0.1)

    # Model selection
    model = opn.DeffuantModel(g)

    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter("epsilon", 0.3)
    config.add_model_parameter("mu", 0.5)

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(50)


.. [#] G. Deffuant, D. Neau, F. Amblard, and G. Weisbuch: "Mixing beliefs among interacting agents." Advances in Complex Systems, 3(01n04):87-98, 2000.
