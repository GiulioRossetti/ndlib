*****
SVEIR
*****

The SVEIR model is a compartmental model designed to study infection dynamics under vaccination campaigns [#]_.

During the simulation, a node can transition from **Susceptible** (S) to **Vaccinated** (V). Susceptible nodes can become **Exposed** (E) upon contact with **Infected** (I) neighbors. Vaccinated nodes can also become exposed, but at a reduced susceptibility rate determined by the vaccine leakage parameter. Exposed nodes incubate the virus before becoming infectious (**Infected**, I), and eventually recover to the **Removed** (R) state.

The transition paths allowed are:

.. math::

    S \to V

.. math::

    S \text{ or } V \to E \to I \to R

--------
Statuses
--------

During the simulation a node can experience the following statuses:

===========  ====
Name         Code
===========  ====
Susceptible  0
Vaccinated   1
Exposed      2
Infected     3
Removed      4
===========  ====

----------
Parameters
----------

=====  =====  ===============  =======  =========  =============================================
Name   Type   Value Type       Default  Mandatory  Description
=====  =====  ===============  =======  =========  =============================================
beta   Model  float in [0, 1]           True       Infection probability
theta  Model  float in [0, 1]           True       Vaccination rate
sigma  Model  float in [0, 1]           True       Vaccine susceptibility leakage (0 is perfect)
delta  Model  float in [0, 1]           True       Incubation (E -> I) rate
gamma  Model  float in [0, 1]           True       Recovery rate
=====  =====  ===============  =======  =========  =============================================

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

-------
Example
-------

In the code below is shown an example of instantiation and execution of a SVEIR simulation on a random graph:

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as ep

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = ep.SVEIRModel(g)

    # Model Configuration
    cfg = mc.Configuration()
    cfg.add_model_parameter('beta', 0.02)
    cfg.add_model_parameter('theta', 0.01)
    cfg.add_model_parameter('sigma', 0.2)
    cfg.add_model_parameter('delta', 0.1)
    cfg.add_model_parameter('gamma', 0.05)
    cfg.add_model_parameter("fraction_infected", 0.05)
    model.set_initial_status(cfg)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] Liu, S. and Zhou, Y., “SVEIR epidemic model with vaccination and temporary immunity,” Applied Mathematics and Computation, vol. 180, no. 1, pp. 314–326, 2006.
