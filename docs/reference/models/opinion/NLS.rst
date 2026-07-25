***************************
Nowak-Lewenstein-Szamrej
***************************

The Nowak-Lewenstein-Szamrej (NLS) model is a discrete threshold opinion dynamics model based on Bibb Latané's Social Impact Theory [#]_ and formally modeled by Andrzej Nowak, Jacek Szamrej, and Michael Lewenstein [#]_.

In the NLS model, individuals hold one of two discrete opinions (modeled as -1 or +1). The psychological impact of the group holding the same opinion (supportive impact :math:`I_S`) and the group holding the opposing opinion (opposing impact :math:`I_O`) on node :math:`i` are computed as:

.. math::

    I_{S, i} = \sum_{j: v_j = v_i} \frac{s_j}{d(j, i)^\alpha}

.. math::

    I_{O, i} = \sum_{k: v_k \neq v_i} \frac{s_k}{d(k, i)^\alpha}

where :math:`s_j` is the social strength (persuasiveness) of node :math:`j`, :math:`d(j, i)` is the shortest network path distance from :math:`j` to :math:`i`, and :math:`\alpha` is the distance decay exponent.

An agent changes their opinion if the net social impact to change exceeds their individual resistance threshold :math:`T_i`:

.. math::

    I_{O, i} - I_{S, i} > T_i

--------
Statuses
--------

During the simulation, a node can experience the following statuses:

===========  ====
Name         Code
===========  ====
Susceptible  0
Infected     1
===========  ====

Note: Opinion status 0 maps to opinion value -1, and Infected status 1 maps to opinion value +1.

----------
Parameters
----------

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

The model configuration parameters:

    - **alpha**: Model Parameter, float, distance decay exponent. Default 2.0.
    - **strength**: Node Parameter, float, persuasiveness. Default 1.0.
    - **threshold**: Node Parameter, float, individual threshold / resistance to opinion change. Default 0.0.

-------
Example
-------

In the code below, we show an example of instantiation and execution of a Nowak-Lewenstein-Szamrej model simulation on a random graph:

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as op

    # Network topology
    g = nx.erdos_renyi_graph(100, 0.2)

    # Model selection
    model = op.NLSModel(g)
    config = mc.Configuration()
    config.add_model_parameter('alpha', 2.0)
    config.add_model_parameter('fraction_infected', 0.3)

    # Add strength and threshold for nodes
    for node in g.nodes():
        config.add_node_configuration('strength', node, 1.0)
        config.add_node_configuration('threshold', node, 0.0)

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(5)


.. [#] B. Latané, “The psychology of social impact,” American Psychologist, vol. 36, no. 4, pp. 343–356, 1981.
.. [#] A. Nowak, J. Szamrej, and M. Latané, “From private attitude to public opinion: A dynamic theory of social impact,” Psychological Review, vol. 97, no. 3, pp. 362–376, 1990.
