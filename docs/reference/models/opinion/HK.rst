*********************
Hegselmann-Krause
*********************

The Hegselmann-Krause model was introduced in 2002 by Hegselmann, Krause et al [#]_.

During each interaction a random  agenti is  selected  and  the  set :math:`\Gamma_{\epsilon}` of  its  neighbors  whose
opinions differ at most :math:`\epsilon` (:math:`d_{i,j}=|x_i(t)-x_j(t)|\leq \epsilon`) is identified.
The selected agent i changes its opinion based on the following update rule:

.. math::

        x_i(t+1)= \frac{\sum_{j \in \Gamma_{\epsilon}} x_j(t)}{\#\Gamma_{\epsilon}}


The idea behind the WHK formulation is that the opinion of agent :math:`i` at time :math:`t+1`, will be given by the average
opinion by its, selected, :math:`\epsilon`-neighbor.

--------
Statuses
--------

Node statuses are continuous values in [-1,1].

----------
Parameters
----------

===========================  =====  =========================  =======  =========  ==============================================
Name                         Type   Value Type                 Default  Mandatory  Description
===========================  =====  =========================  =======  =========  ==============================================
epsilon                      Model  float in [0, 1]             ---     True       Bounded confidence threshold
===========================  =====  =========================  =======  =========  ==============================================


-------
Example
-------

In the code below is shown an example of instantiation and execution of an HK model simulation on a random graph:
we an epsilon value of 0.32 .


.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.opinions as opn

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = opn.HKModel(g)

    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter("epsilon", 0.32)

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(20)


.. [#] R. Hegselmann, U. Krause, et al.: “Opinion dynamics and bounded confidence models, analysis, and simulation." in Journal of artificial societies and social simulation, 2002
