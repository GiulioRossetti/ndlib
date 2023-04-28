**************************
Cognitive Opinion Dynamics
**************************

The Cognitive Opinion Dynamics model was introduced in [#]_, which models the state of individuals taking into account several cognitively-grounded variables. 

The aim of the model is to simulate response to risk in catastrophic events in the presence of external (institutional) information. 

The individual opinion is modelled as a continuous variable **Oi** ∈ [0, 1], representing the degree of perception of the risk (how probable it is that the catastrophic event will actually happen). 

This opinion evolves through interactions with neighbours and external information, based on four internal variables for each individual i: 

- risk sensitivity (Ri ∈ {−1, 0, 1}), 
- tendency to inform others (βi ∈ [0,1]), 
- trust in institutions (Ti ∈ [0,1]), and
-  trust in peers (Πi = 1 − Ti). 

These values are generated when the population is initialised and stay fixed during the simulation. 

The update rules define how **Oi** values change in time.

The model was shown to be able to reproduce well various real situations. In particular, it is visible that risk sensitivity is more important than trust in institutional information when it comes to evaluating risky situations.


--------
Statuses
--------

Node statuses are continuous values in [0,1].

----------
Parameters
----------

===================  =====  ================  =======  =========  =============================================
Name                 Type   Value Type        Default  Mandatory  Description
===================  =====  ================  =======  =========  =============================================
I                    Model  float in [0, 1]            True       External information
T_range_min          Model  float in [0, 1]            True       Minimum of the range of initial values for T
T_range_max          Model  float in [0, 1]            True       Maximum of the range of initial values for T
B_range_min          Model  float in [0, 1]            True       Minimum of the range of initial values for B
B_range_max          Model  float in [0, 1]            True       Maximum of the range of initial values for B
R_fraction_negative  Model  float in [0, 1]            True       Fraction of nodes having R=-1
R_fraction_neutral   Model  float in [0, 1]            True       Fraction of nodes having R=0
R_fraction_positive  Model  float in [0, 1]            True       Fraction of nodes having R=1
===================  =====  ================  =======  =========  =============================================

The following relation should hold: ``R_fraction_negative+R_fraction_neutral+R_fraction_positive=1``.
To achieve this, the fractions selected will be normalised to sum 1.

The initial state is generated randomly uniformly from the domain defined by model parameters.

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

The two options are mutually exclusive and the latter takes precedence over the former.

-------
Example
-------

In the code below is shown an example of instantiation and execution of a Cognitive Opinion Dynamics model simulation on a random graph: we set the initial infected node set to the 10% of the overall population, the external information value to 015, the B and T intervals equal to [0,1] and the fraction of positive/neutral/infected equal to 1/3.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as op

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = op.CognitiveOpDynModel(g)

    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter("I", 0.15)
    config.add_model_parameter("B_range_min", 0)
    config.add_model_parameter("B_range_max", 1)
    config.add_model_parameter("T_range_min", 0)
    config.add_model_parameter("T_range_max", 1)
    config.add_model_parameter("R_fraction_negative", 1.0 / 3)
    config.add_model_parameter("R_fraction_neutral", 1.0 / 3)
    config.add_model_parameter("R_fraction_positive", 1.0 / 3)
    config.add_model_parameter('fraction_infected', 0.1)
    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] D. Vilone, F. Giardini, M. Paolucci, and R. Conte, “Reducing individuals’ risk sensitiveness can promote positive and non-alarmist views about catastrophic events in an agent-based simulation,” arXiv preprint arXiv:1609.04566, 2016.
