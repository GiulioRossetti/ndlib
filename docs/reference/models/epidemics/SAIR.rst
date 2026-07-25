****
SAIR
****

The SAIR model is a compartmental model that splits the infected population into Asymptomatic and Symptomatic classes [#]_.

During the course of the simulation, a node can transition from **Susceptible** (S) to either **Asymptomatic** (A) or **Infected** (I, symptomatic). From both classes, nodes eventually recover and transition to the **Removed** (R) state.

The transition sequence allowed is:

.. math::

    S \to A \text{ or } I \to R

--------
Statuses
--------

During the simulation a node can experience the following statuses:

===========  ====
Name         Code
===========  ====
Susceptible  0
Asymptomatic 1
Infected     2
Removed      3
===========  ====

----------
Parameters
----------

=======  =====  ===============  =======  =========  =============================================
Name     Type   Value Type       Default  Mandatory  Description
=======  =====  ===============  =======  =========  =============================================
beta     Model  float in [0, 1]           True       Infection probability from Symptomatic nodes
beta_a   Model  float in [0, 1]           True       Infection probability from Asymptomatic nodes
p        Model  float in [0, 1]           True       Probability of developing symptoms
gamma_i  Model  float in [0, 1]           True       Recovery probability for Symptomatic nodes
gamma_a  Model  float in [0, 1]           True       Recovery probability for Asymptomatic nodes
=======  =====  ===============  =======  =========  =============================================

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

-------
Example
-------

In the code below is shown an example of instantiation and execution of a SAIR simulation on a random graph:

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as ep

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = ep.SAIRModel(g)

    # Model Configuration
    cfg = mc.Configuration()
    cfg.add_model_parameter('beta', 0.02)
    cfg.add_model_parameter('beta_a', 0.01)
    cfg.add_model_parameter('p', 0.5)
    cfg.add_model_parameter('gamma_i', 0.05)
    cfg.add_model_parameter('gamma_a', 0.05)
    cfg.add_model_parameter("fraction_infected", 0.05)
    model.set_initial_status(cfg)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] Robinson, M. and Stilianakis, N.I., “A three-state compartmental model for influenza epidemics,” Mathematical Medicine and Biology: A Journal of the IMA, vol. 30, no. 2, pp. 147–160, 2013.
