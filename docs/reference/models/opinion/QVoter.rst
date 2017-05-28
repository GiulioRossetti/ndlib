*******
Q-Voter
*******

The Q-Voter model was introduced as a generalisation of discrete opinion dynamics models [#]_. 

Here, N individuals hold an opinion ±1. 
At each time step, a set of **q** neighbours are chosen and, if they agree, they influence one neighbour chosen at random, i.e. this agent copies the opinion of the group. 
If the group does not agree, the agent flips its opinion with probability ε. 

It is clear that the voter and Sznajd models are special cases of this more recent model (q = 1,ε = 0 and q = 2,ε = 0). 

Analytic results for q ≤ 3 validate the numerical results obtained for the special case models, with transitions from a ordered phase (small ε) to a disordered one (large ε). 
For q > 3, a new type of transition between the two phases appears, which consist of passing through an intermediate regime where the final state depends on the initial condition. We implemented in NDlib the model with ε = 0.


.. autoclass:: ndlib.models.opinions.QVoterModel.QVoterModel
.. automethod:: ndlib.models.opinions.QVoterModel.QVoterModel.__init__(graph)


-------
Example
-------

In the code below is shown an example of istantiation and execution of a Q-Voter model simultion on a random graph: we set the initial infected node set to the 10% of the overall population and the number **q** of influencing neighbors equals to 5.

.. code-block:: python
    :linenos:

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions.QVoterModel as qvt

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = qvt.QVoterModel(g)
    config = mc.Configuration()
    config.add_model_parameter("q", 5)
    config.add_model_parameter('percentage_infected', 0.1)
    
    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] C. Castellano, M. A. Munoz, and R. Pastor-Satorras, “The non-linear q-voter model,” Physical Review E, vol. 80, p. 041129, 2009.