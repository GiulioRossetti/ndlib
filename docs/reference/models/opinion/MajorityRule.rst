*************
Majority Rule
*************

The Majority Rule model is a discrete model of opinion dynamics, proposed to describe public debates [#]_. 

Agents take discrete opinions ±1, just like the Voter model. 
At each time step a group of **r** agents is selected randomly and they all take the majority opinion within the group. 

The group size can be fixed or taken at each time step from a specific distribution. 
If **r** is odd, then the majority opinion is always defined, however if **r** is even there could be tied situations. To select a prevailing opinion in this case, a bias in favour of one opinion (+1) is introduced. 

This idea is inspired by the concept of social inertia [#]_.

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

=========  =====  ================  =======  =========  =====================
Name       Type   Value Type        Default  Mandatory  Description
=========  =====  ================  =======  =========  =====================
q          Model  int in [0, V(G)]           True       Number of neighbours
=========  =====  ================  =======  =========  =====================

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

The two options are mutually exclusive and the latter takes precedence over the former.


-------
Example
-------

In the code below is shown an example of instantiation and execution of a Majority Rule model simulation on a random graph: we set the initial infected node set to the 10% of the overall population.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as op

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = op.MajorityRuleModel(g)
    config = mc.Configuration()
    config.add_model_parameter('fraction_infected', 0.1)
    
    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] S.Galam, “Minority opinion spreading in random geometry.” Eur.Phys. J. B, vol. 25, no. 4, pp. 403–406, 2002.
.. [#] R.Friedman and M.Friedman, "The Tyranny of the Status Quo." Orlando, FL, USA: Harcourt  Brace Company, 1984.
