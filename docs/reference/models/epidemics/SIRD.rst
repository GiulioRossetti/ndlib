****
SIRD
****

The SIRD model is an extension of the classical SIR model [#]_ that explicitly models disease mortality.

In this model, during the course of an epidemic, a node changes its status from **Susceptible** (S) to **Infected** (I). From the infected state, the node can transition either to **Removed** (R, recovered/immune) or to **Deaths** (D, deceased).

The transition sequence allowed is:

.. math::

    S \to I \to R \text{ or } D

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
Deaths       3
===========  ====

----------
Parameters
----------

=====  =====  ===============  =======  =========  =====================
Name   Type   Value Type       Default  Mandatory  Description
=====  =====  ===============  =======  =========  =====================
beta   Model  float in [0, 1]           True       Infection probability
gamma  Model  float in [0, 1]           True       Recovery probability
mu     Model  float in [0, 1]           True       Mortality probability
=====  =====  ===============  =======  =========  =====================

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

-------
Example
-------

In the code below is shown an example of instantiation and execution of a SIRD simulation on a random graph:

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as ep

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = ep.SIRDModel(g)

    # Model Configuration
    cfg = mc.Configuration()
    cfg.add_model_parameter('beta', 0.01)
    cfg.add_model_parameter('gamma', 0.005)
    cfg.add_model_parameter('mu', 0.001)
    cfg.add_model_parameter("fraction_infected", 0.05)
    model.set_initial_status(cfg)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] W. O. Kermack and A. McKendrick, “A Contribution to the Mathematical Theory of Epidemics,” Proceedings of the Royal Society of London. Series A, Containing Papers of a Mathematical and Physical Character, vol. 115, no. 772, pp. 700–721, Aug. 1927
