**************************************************
Independent Cascades with Community Embeddedness
**************************************************

The Independent Cascades with Community Embeddedness model was introduced by Milli and Rossetti in 2019 [#]_.

This model is a variation of the well-known Independent Cascade (IC), and it is designed to embed community awareness into the IC model.
The probability p(u,v) of the IC model is replaced by the edge embeddedness.

The embeddedness of an edge :math:`(u,v)` with :math:`u,v \in C` is defined as:
:math:`e_{u,v} = \frac{\phi_{u,v}}{|\Gamma(u) \cup \Gamma(v)|}`
where :math:`\phi_{u,v}` is the number of common neighbors of u and v within :math:`C`, and :math:`\Gamma(u)` ( :math:`\Gamma(v)`) is the set of neighbors of the node u (v) in the analyzed graph G.

The ICE model starts with an initial set of **active** nodes A0; the diffusive process unfolds in discrete steps according to the following randomized rule:

- When node v becomes active in step t, it is given a single chance to activate each currently inactive neighbor u. If v and u belong to the same community, it succeeds with a probability :math:`e_{u,v}`; otherwise with probability :math:`\min\{e_{z,v}|(z, v)\in E\}`.
- If u has multiple newly activated neighbors, their attempts are sequenced in an arbitrary order.
- If v succeeds, then u will become active in step t + 1; but whether or not v succeeds, it cannot make any further attempts to activate u in subsequent rounds.
- The process runs until no more activations are possible.

--------
Statuses
--------

During the simulation a node can experience the following statuses:

===========  ====
Name         Code
===========  ====
Susceptible  0
Infected     1
Removed      2
===========  ====


----------
Parameters
----------

The model is parameter free

The initial infection status can be defined via:

    - **fraction_infected**: Model Parameter, float in [0, 1]
    - **Infected**: Status Parameter, set of nodes

The two options are mutually exclusive and the latter takes precedence over the former.

-------
Example
-------

In the code below is shown an example of instantiation and execution of an ICE model simulation on a random graph: we set the initial set of infected nodes as 1% of the overall population.


.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics as ep

    # Network topology
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Model selection
    model = ep.ICEModel(g)

    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter('fraction_infected', 0.1)

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(200)


.. [#] L. Milli and G. Rossetti. “Community-Aware Content Diffusion: Embeddednes and Permeability,” in Proceedings of International Conference on Complex Networks and Their Applications, 2019 pp. 362--371.