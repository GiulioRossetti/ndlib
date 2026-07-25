********
Altafini
********

The Altafini model is a continuous opinion dynamics model on signed networks introduced by Claudio Altafini [#]_.

In signed networks, edges represent positive (trust, friendship) or negative (distrust, hostility) relationships. In the Altafini model, the signs of edges dictate how agents update their opinions. When interacting, an agent adopts the opinion of a neighbor if the link is positive, and adopts the negative of their opinion if the link is negative:

.. math::

    x_i(t+1) = \sum_{j \in \text{neigh}(i)} W_{ij} \text{sgn}(A_{ij}) x_j(t)

where :math:`A_{ij}` represents the signed relationship. In the unweighted network implementation, this becomes a simple average:

.. math::

    x_i(t+1) = \frac{1}{\text{deg}(i)} \sum_{j \in \text{neigh}(i)} A_{ij} x_j(t)

with :math:`A_{ij} \in \{-1, +1\}`.

--------
Statuses
--------

During the simulation, a node can experience the following statuses:

=========  ====
Name       Code
=========  ====
Infected   0
=========  ====

Note: The opinion is represented as a continuous value in [-1, 1] corresponding to the Infected status.

----------
Parameters
----------

    - **init_dist_lower**: Model Parameter, float, lower bound of initial opinion distribution. Default -1.
    - **init_dist_upper**: Model Parameter, float, upper bound of initial opinion distribution. Default 1.
    - **sign**: Edge Parameter, int in {-1, 1}, representing trust (+1) or distrust (-1) relations. Default 1.

-------
Example
-------

In the code below, we show an example of instantiation and execution of an Altafini model simulation on a random graph:

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as op

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = op.AltafiniModel(g)
    config = mc.Configuration()
    config.add_model_parameter('init_dist_lower', -1.0)
    config.add_model_parameter('init_dist_upper', 1.0)

    # Add signs for edges
    for edge in g.edges():
        config.add_edge_configuration('sign', edge, 1)

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(10)


.. [#] C. Altafini, “Consensus problems on networks with antagonistic interactions,” IEEE Transactions on Automatic Control, vol. 58, no. 4, pp. 935–946, 2013.
