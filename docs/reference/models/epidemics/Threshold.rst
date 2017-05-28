*********
Threshold
*********

The Threshold model was introduced in 1978 by Granovetter [#]_. 

In this model during an epidemics, a node has two distinct and mutually exclusive behavioral alternatives, e.g., the decision to do or not do something, to participate or not participate in a riot. 

Node's individual decision depends on the percentage of its neighbors have made the same choice, thus imposing a threshold. 

The model works as follows: 
- each node has its own threshold; 
- during a generic iteration every node is observed: iff the percentage of its infected neighbors is grater than its threshold it becomes infected as well.

.. autoclass:: ndlib.models.epidemics.ThresholdModel.ThresholdModel
.. automethod:: ndlib.models.epidemics.ThresholdModel.ThresholdModel.__init__(graph)

=======
Example
=======

In the code below is shown an example of istantiation and execution of a Threshold model simultion on a random graph: we set the initial set of infected nodes as 1% of the overall population, and assign a threshold of 0.25 to all the nodes.


.. code-block:: python
    :linenos:

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics.ThresholdModel as th

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = th.ThresholdModel(g)
        
    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter('percentage_infected', 0.1)

    # Setting node parameters
    threshold = 0.25
    for i in g.nodes():
        config.add_node_configuration("threshold", i, threshold)

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] M. Granovetter, “Threshold models of collective behavior,” The American Journal of Sociology, vol. 83, no. 6, pp. 1420–1443, 1978.