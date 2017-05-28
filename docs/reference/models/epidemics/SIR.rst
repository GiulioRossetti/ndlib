***
SIR
***

The SIR model was introduced in 1927 by Kermack [#]_.
 
In this model, during the course of an epidemics, a node is allowed to change its status  from **Susceptible** (S) to **Infected** (I), then to **Removed** (R).

The model is instantiated on a graph having a non-empty set of infected nodes.

SIR assumes that if, during a generic iteration, a susceptible node comes into contact with an infected one, it becomes infected with probability beta, than it can be switch to removed with probability gamma (the only transition allowed are S→I→R).

.. autoclass:: ndlib.models.epidemics.SIRModel.SIRModel
.. automethod:: ndlib.models.epidemics.SIRModel.SIRModel.__init__(graph)

=======
Example
=======

In the code below is shown an example of istantiation and execution of an SIR simultion on a random graph: we set the initial set of infected nodes as 5% of the overall population, a probability of infection of 1%, and a removal probability of 0.5%.

.. code-block:: python
    :linenos:

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics.SIRModel as sir

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = sir.SIRModel(g)

    # Model Configuration
    cfg = mc.Configuration()
    cfg.add_model_parameter('beta', 0.01)
    cfg.add_model_parameter('gamma', 0.005)
    cfg.add_model_parameter("percentage_infected", 0.05)
    model.set_initial_status(cfg)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] W. O. Kermack and A. McKendrick, “A Contribution to the Mathemat- ical Theory of Epidemics,” Proceedings of the Royal Society of London. Series A, Containing Papers of a Mathematical and Physical Character, vol. 115, no. 772, pp. 700–721, Aug. 1927