******************
Voter with Zealots
******************

The Voter model with Zealots is a discrete opinion dynamics model extending the classical Voter model [#]_ [#]_ [#]_.

In this model, a fraction of the population are designated as "zealots" (stubborn agents) who hold fixed, immutable opinions. During each iteration, a random individual (listener) is selected:
- If the listener is a zealot, their opinion remains unchanged.
- If the listener is a normal agent, they pick a random neighbor (speaker) and copy their opinion.

The introduction of zealots prevents complete consensus in finite networks, instead leading to stationary states where opinions fluctuate around stable averages determined by the concentration and distribution of zealots.

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

----------
Parameters
----------

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

The stubborn nodes are configured via:

    - **zealot**: Node Parameter, int in {0, 1}, indicating whether the node is a stubborn agent (1) or a normal agent (0). Default 0.

-------
Example
-------

In the code below, we show an example of instantiation and execution of a Voter model with Zealots simulation on a random graph:

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as op

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = op.VoterZealotModel(g)
    config = mc.Configuration()
    config.add_model_parameter('fraction_infected', 0.2)

    # Set first 10 nodes as zealots
    for i, node in enumerate(g.nodes()):
        config.add_node_configuration('zealot', node, 1 if i < 10 else 0)

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] P. Clifford and A. Sudbury, “A model for spatial conflict,” Biometrika, vol. 60, no. 3, pp. 581–588, 1973.
.. [#] R. Holley and T. Liggett, “Ergodic theorems for weakly interacting infinite systems and the voter model,” Ann. Probab., vol. 3, no. 4, pp. 643–663, 1975.
.. [#] M. Mobilia, “Does a single zealot affect an infinite group of voters?,” Physical Review Letters, vol. 91, no. 2, p. 028701, 2003.
