****************************
Algorithmic Bias Media Model
****************************

The Algorithmic Bias Media model considers a population of individuals, where each individual holds a continuous opinion  in the interval  [0,1].
Additional elements in the population are the media, which are characterized by a fixed opinion value.
Individuals are connected by a social network, and interact pairwise at discrete time steps.
The interacting pair is selected from the population at each time point in such a way that individuals that have close opinion values are selected more often, to simulate algorithmic bias.
The parameter gamma controls how large this effect is.
Specifically, the first individual in the interacting pair is selected randomly, while the second individual is selected based on a probability that decreases with the distance from the opinion of the first individual, i.e. directly proportional with the distance raised to the power -gamma.
Moreover, the media interaction are selected with a fixed probability at each time step.

After interaction, the two opinions may change, depending on a so called bounded confidence parameter, epsilon.
This can be seen as a measure of the open-mindedness of individuals in a population.

It defines a threshold on the distance between the opinion of the two individuals, beyond which communication between individuals is not possible due to conflicting views.
Thus, if the distance between the opinions of the selected individuals is lower than epsilon, the two individuals adopt their average opinion. Otherwise nothing happens.

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
gamma_media          Model  int in [0, 100]            True       Algorithmic bias for media
p                    Model  float in [0, 1]            True       Probability of media interaction
k                    Model  int in [0, |V|]            True       Number of media
===================  =====  ================  =======  =========  =============================================

-------
Example
-------

In the code below is shown an example of instantiation and execution of a Algorithmic Bias Media model simulation on a random graph with 2 media and a agent-media interaction probability of 5%.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as op

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = op.AlgorithmicBiasMediaModel(g)

    # Model configuration
    config = mc.Configuration()
    config.add_model_parameter("epsilon", 0.32)
    config.add_model_parameter("gamma", 1)
    config.add_model_parameter("k", 2)
    config.add_model_parameter("p", 0.05)
    config.add_model_parameter("gamma_media", 0.1)
    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


