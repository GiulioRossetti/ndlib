***
SIR
***

The SIR model was introduced in 1927 by Kermack [#]_.
 
In this model, during the course of an epidemics, a node is allowed to change its status  from **Susceptible** (S) to **Infected** (I), then to **Removed** (R).

The model is instantiated on a graph having a non-empty set of infected nodes.

SIR assumes that if, during a generic iteration, a susceptible node comes into contact with an infected one, it becomes infected with probability beta, than it can be switch to removed with probability gamma (the only transition allowed are S→I→R).

The dSIR implementation assumes that the process occurs on a directed/undirected dynamic network; this model was introduced by Milli et al. in 2018 [#]_.

--------
Statuses
--------

During the simulation a node can experience the following statuses:

===========  ====
Name         Code
===========  ====
Susceptible  0
Infected     1
Removed      2
===========  ====

----------
Parameters
----------

=====  =====  ===============  =======  =========  =====================
Name   Type   Value Type       Default  Mandatory  Description
=====  =====  ===============  =======  =========  =====================
beta   Model  float in [0, 1]           True       Infection probability
gamma  Model  float in [0, 1]           True       Removal probability
=====  =====  ===============  =======  =========  =====================

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

The two options are mutually exclusive and the latter takes precedence over the former.

-------
Example
-------

In the code below is shown an example of instantiation and execution of an DynSIR simulation on a dynamic random graph: we set the initial set of infected nodes as 5% of the overall population, a probability of infection of 1%, and a removal probability of 1%.

.. code-block:: python

    import networkx as nx
    import dynetx as dn
    import ndlib.models.ModelConfig as mc
    import ndlib.models.dynamic as dm
    from past.builtins import xrange

    # Dynamic Network topology
    dg = dn.DynGraph()

    for t in xrange(0, 3):
        g = nx.erdos_renyi_graph(200, 0.05)
        dg.add_interactions_from(g.edges(), t)

    # Model selection
    model = dm.DynSIRModel(dg)

    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter('beta', 0.01)
    config.add_model_parameter('gamma', 0.01)
    config.add_model_parameter("fraction_infected", 0.1)
    model.set_initial_status(config)

    # Simulate snapshot based execution
    iterations = model.execute_snapshots()

    # Simulation interaction graph based execution
    iterations = model.execute_iterations()


.. [#] W. O. Kermack and A. McKendrick, “A Contribution to the Mathematical Theory of Epidemics,” Proceedings of the Royal Society of London. Series A, Containing Papers of a Mathematical and Physical Character, vol. 115, no. 772, pp. 700–721, Aug. 1927
.. [#] Letizia Milli, Giulio Rossetti, Fosca Giannotti, Dino Pedreschi. “Diffusive Phenomena in Dynamic Networks: a data-driven study”. Accepted to International Conference on Complex Networks (CompleNet), 2018, Boston.
