****************
Algorithmic Bias
****************

The Algorithmic Bias model considers a population of individuals, where each individual holds a continuous opinion  in the interval  [0,1].
Individuals are connected by a social network, and interact pairwise at discrete time steps.
The interacting pair is selected from the population at each time point in such a way that individuals that have close opinion values are selected more often, to simulate algorithmic bias.
The parameter gamma controls how large this effect is.
Specifically, the first individual in the interacting pair is selected randomly, while the second individual is selected based on a probability that decreases with the distance from the opinion of the first individual, i.e. directly proportional with the distance raised to the power -gamma.


After interaction, the two opinions may change, depending on a so called bounded confidence parameter, epsilon.
This can be seen as a measure of the open-mindedness of individuals in a population.
It defines a threshold on the distance between the opinion of the two individuals, beyond which communication between individuals is not possible due to conflicting views.
Thus, if the distance between the opinions of the selected individuals is lower than epsilon, the two individuals adopt their average opinion. Otherwise nothing happens.

Note: setting gamma=0 reproduce the results for the Deffuant model.

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
epsilon              Model  float in [0, 1]            True       Bounded confidence threshold
gamma                Model  int in [0, 100]            True       Algorithmic bias
===================  =====  ================  =======  =========  =============================================

-------
Example
-------

In the code below is shown an example of instantiation and execution of a AlgorithmicBiasModel model simulation on a random graph: we set the initial infected node set to the 10% of the overall population.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as op

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = op.AlgorithmicBiasModel(g)

    # Model configuration
    config = mc.Configuration()
    config.add_model_parameter("epsilon", 0.32)
    config.add_model_parameter("gamma", 1)
    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


