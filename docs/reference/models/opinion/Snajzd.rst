******
Sznajd
******

The Sznajd model [#]_ is a variant of spin model employing the theory of social impact, which takes into account the fact that a group of individuals with the same opinion can influence their neighbours more than one single individual. 

In the original model the social network is a 2-dimensional lattice, however we also implemented the variant on any complex networks. 

Each agent has an opinion σi = ±1. 
At each time step, a pair of neighbouring agents is selected and, if their opinion coincides, all their neighbours take that opinion. 

The model has been shown to converge to one of the two agreeing stationary states, depending on the initial density of up-spins (transition at 50% density).


.. autoclass:: ndlib.models.opinions.SznajdModel.SznajdModel
.. automethod:: ndlib.models.opinions.SznajdModel.SznajdModel.__init__(graph)


-------
Example
-------

In the code below is shown an example of istantiation and execution of a Sznajd model simultion on a random graph: we set the initial infected node set to the 10% of the overall population.

.. code-block:: python
    :linenos:

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions.SznajdModel as sn

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = sn.SznajdModel(g)
    config = mc.Configuration()
    config.add_model_parameter('percentage_infected', 0.1)
    
    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] K. Sznajd-Weron and J. Sznajd, “Opinion evolution in closed community,” International Journal of Modern Physics C, vol. 11, pp. 1157–1165, 2001.
