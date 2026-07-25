****
SIRS
****

The SIRS model is an extension of the classical SIR model [#]_.

In this model, during the course of an epidemic, a node changes its status from **Susceptible** (S) to **Infected** (I), then to **Removed** (R), and finally back to **Susceptible** (S) after immunity wanes.

The transition sequence allowed is:

.. math::

    S \to I \to R \to S

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

=====  =====  ===============  =======  =========  =========================
Name   Type   Value Type       Default  Mandatory  Description
=====  =====  ===============  =======  =========  =========================
beta   Model  float in [0, 1]           True       Infection probability
gamma  Model  float in [0, 1]           True       Recovery probability
eta    Model  float in [0, 1]           True       Waning immunity probability
=====  =====  ===============  =======  =========  =========================

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

-------
Example
-------

In the code below is shown an example of instantiation and execution of a SIRS simulation on a random graph:

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as ep

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = ep.SIRSModel(g)

    # Model Configuration
    cfg = mc.Configuration()
    cfg.add_model_parameter('beta', 0.01)
    cfg.add_model_parameter('gamma', 0.005)
    cfg.add_model_parameter('eta', 0.01)
    cfg.add_model_parameter("fraction_infected", 0.05)
    model.set_initial_status(cfg)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] W. O. Kermack and A. McKendrick, “A Contribution to the Mathematical Theory of Epidemics,” Proceedings of the Royal Society of London. Series A, Containing Papers of a Mathematical and Physical Character, vol. 115, no. 772, pp. 700–721, Aug. 1927
