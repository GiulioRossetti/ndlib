*********
SEIS (CT)
*********


In the SEIS model, during the course of an epidemics, a node is allowed to change its status  from **Susceptible** (S) to **Exposed** (E) to **Infected** (I), then again to **Susceptible** (S).

The model is instantiated on a graph having a non-empty set of infected nodes.

SEIS assumes that if, during a generic iteration, a susceptible node comes into contact with an infected one, it becomes infected after an exposition period with probability beta, than it can switch back to susceptible with probability lambda (the only transition allowed are S→E→I→S).

This implementation assumes continuous time dynamics for the E->I  and I->S transitions.

--------
Statuses
--------

During the simulation a node can experience the following statuses:

===========  ====
Name         Code
===========  ====
Susceptible  0
Infected     1
Exposed		 2
===========  ====

----------
Parameters
----------

======  =====  ===============  =======  =========  =====================
Name    Type   Value Type       Default  Mandatory  Description
======  =====  ===============  =======  =========  =====================
beta    Model  float in [0, 1]           True       Infection probability
lambda  Model  float in [0, 1]           True       Removal probability
alpha   Model  float in [0, 1]           True       Latent period
======  =====  ===============  =======  =========  =====================

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

The two options are mutually exclusive and the latter takes precedence over the former.

-------
Example
-------

In the code below is shown an example of instantiation and execution of an SEIS simulation on a random graph:
we set the initial set of infected nodes as 5% of the overall population, a probability of infection of 1%, a removal probability of 0.5% and an latent period of 5% (e.g. 20 iterations).

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as ep

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = ep.SEISctModel(g)

    # Model Configuration
    cfg = mc.Configuration()
    cfg.add_model_parameter('beta', 0.01)
    cfg.add_model_parameter('lambda', 0.005)
    cfg.add_model_parameter('alpha', 0.05)
    cfg.add_model_parameter("fraction_infected", 0.05)
    model.set_initial_status(cfg)

    # Simulation execution
    iterations = model.iteration_bunch(200)


