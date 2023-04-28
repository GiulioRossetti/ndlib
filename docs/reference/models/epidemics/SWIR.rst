****
SWIR
****
The SWIR model was introduced in 2017 by Lee et al. [#]_.
 
In this model, during the epidemics, a node is allowed to change its status from **Susceptible** (S) to **Weakened** (W) or **Infected** (I), then to **Removed** (R).

The model is instantiated on a graph having a non-empty set of infected nodes.

At time *t* a node in the state I is selected randomly and the states of all neighbors are checked one by one. If the state of a neighbor is S then this state changes either i) to I with probability *kappa* or ii) to W with probability *mu*. If the state of a neighbor is W then the state W changes to I with probability *nu*. We repeat the above process for all nodes in state I and then changes to R for each associated node. 

--------
Statuses
--------

During the simulation a node can experience the following statuses:

===========  ====
Name         Code
===========  ====
Susceptible  0
Infected     1
Weakened	 2
Removed      3
===========  ====

----------
Parameters
----------

=====  =====  ===============  =======  =========  =====================
Name   Type   Value Type       Default  Mandatory  Description
=====  =====  ===============  =======  =========  =====================
kappa  Model  float in [0, 1]           True
mu     Model  float in [0, 1]           True
nu     Model  float in [0, 1]           True
=====  =====  ===============  =======  =========  =====================

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

The two options are mutually exclusive and the latter takes precedence over the former.

-------
Example
-------

In the code below is shown an example of instantiation and execution of an SEIR simulation on a random graph: we set the initial set of infected nodes as % of the overall population, a probability of infection of 1%, a removal probability of 0.5% and an latent period of 5% (e.g. 20 iterations).

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as ep

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = ep.SWIRModel(g)

    # Model Configuration
    cfg = mc.Configuration()
    cfg.add_model_parameter('kappa', 0.01)
    cfg.add_model_parameter('mu', 0.005)
    cfg.add_model_parameter('nu', 0.05)
    cfg.add_model_parameter("fraction_infected", 0.05)
    model.set_initial_status(cfg)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] D. Lee, W. Choi, J. Kertész, B. Kahng. “Universal mechanism for hybrid percolation transitions”. Scientific Reports, vol. 7(1), 5723, 2017.
