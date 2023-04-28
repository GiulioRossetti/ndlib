*****
Voter
*****

The Voter model is one of the simplest models of opinion dynamics, originally introduced to analyse competition of species [#]_ and soon after applied to model elections [#]_. 

The model assumes the opinion of an individual to be a discrete variable ±1. 

The state of the population varies based on a very simple update rule: at each iteration, a random individual is selected, who then copies the opinion of one random neighbour. 

Starting from any initial configuration, on a complete network the entire population converges to consensus on one of the two options. The probability that consensus is reached on opinion +1 is equal to the initial fraction of individuals holding that opinion [#]_.


--------
Statuses
--------

During the simulation a node can experience the following statuses:

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

The initial blocked nodes can be defined via:

    - **percentage_blocked**: Model Parameter, float in [0, 1]
    - **Blocked**: Status Parameter, set of nodes

In both cases, the two options are mutually exclusive and the latter takes precedence over the former.


-------
Example
-------

In the code below is shown an example of instantiation and execution of a Voter model simulation on a random graph: we set the initial infected node set to the 10% of the overall population.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as op

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = op.VoterModel(g)
    config = mc.Configuration()
    config.add_model_parameter('fraction_infected', 0.1)
    
    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] P. Clifford and A. Sudbury, “A model for spatial conflict,” Biometrika, vol. 60, no. 3, pp. 581–588, 1973.
.. [#] R. Holley and T. Liggett, “Ergodic theorems for weakly interacting infinite systems and the voter model,” Ann. Probab., vol. 3, no. 4, pp. 643–663, Aug 1975.
.. [#] P.L.Krapivsky,S.Redner,andE.Ben-Naim,Akineticviewofstatistical physics. Cambridge University Press, 2010.
