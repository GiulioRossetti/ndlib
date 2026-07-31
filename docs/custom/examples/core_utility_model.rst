******************************
Core and Utility Model Example
******************************

This example shows how the core blocks and the utility blocks can be combined
to bootstrap a custom model in Python. The code mirrors the same block objects
that the dashboard generator emits, but keeps the construction explicit so it is
easy to adapt in a hand-written model.

.. code-block:: python

   import networkx as nx

   from ndlib.models.compartments.NDQLBlocks import (
       Aggregator,
       AttributeInitializer,
       ClampNormalize,
       Compose,
       CommunityAssignment,
       Constant,
       Distribution,
       Filter,
       Kernel,
       NodeRoleAssignment,
       Observe,
       Parameter,
       PreviewObservable,
       RuleAlias,
       Schedule,
       SeedSelection,
       Selector,
       Transform,
       ValidationHint,
       Variable,
   )

   graph = nx.erdos_renyi_graph(12, 0.25, seed=3)
   for node in graph.nodes():
       graph.nodes[node]["community"] = 0 if node < 6 else 1

   status = {node: 0.0 for node in graph.nodes()}
   params = {"model": {"iteration": 0, "available_statuses": {"Susceptible": 0, "Infected": 1}}}

   beta = Parameter(name="beta", value=0.18, type="float", scope="model")
   seed_value = Constant(name="seed_value", value=7, type="int")
   opinion = Variable(name="opinion", scope="node", type="continuous", range=[0, 1], default=0.5)
   init_dist = Distribution(
       family="bimodal",
       params={"low": 0.2, "high": 0.8, "sigma": 0.05, "mix": 0.5},
       bounds=[0, 1],
   )

   selector = Selector(policy="random", share=0.25)
   gate = Filter(predicate="opinion >= 0.5")
   neighbor_mean = Aggregator(mode="mean", variable="opinion", target="neighbor_mean")
   drift = Kernel(rate=beta.resolve(), clamp=True)
   transition = Compose(
       condition=gate,
       if_true=Transform(expression="min(1.0, opinion + beta)", target="opinion"),
       if_false=Transform(expression="max(0.0, opinion - beta / 2)", target="opinion"),
   )
   schedule = Schedule(start=0, end=20, period=1)
   observe = Observe(variable="opinion", mode="bins", bins=12, range=[0, 1])
   clip = ClampNormalize(min=0.0, max=1.0, target="opinion")

   seed_nodes = SeedSelection(nodes=[0, 5], target="seed_nodes")
   roles = NodeRoleAssignment(role="seed", nodes=[0, 5], target="role")
   init_attr = AttributeInitializer(attribute="opinion", value=0.5, scope="node")
   communities = CommunityAssignment(
       community_map={node: graph.nodes[node]["community"] for node in graph.nodes()},
       field="community",
       target="com",
   )
   alias = RuleAlias(
       alias="opinion_seed_pipeline",
       target="opinion",
       description="Seed and initialize opinions",
   )
   preview = PreviewObservable(variable="opinion", mode="bins", bins=12, range=[0, 1])
   hint = ValidationHint(name="opinion", minimum=0.0, maximum=1.0, target="opinion")

   opinions = init_dist.sample(size=graph.number_of_nodes())
   for node, value in zip(graph.nodes(), opinions):
       graph.nodes[node]["opinion"] = float(value)

   # Utility blocks can stamp the graph with metadata before the model runs.
   seed_nodes.execute(0, graph, status, status, params)
   roles.execute(0, graph, status, status, params)
   communities.execute(0, graph, status, status, params)
   init_attr.execute(0, graph, status, status, params)
   preview.execute(0, graph, status, status, params)
   hint.execute(0, graph, status, status, params)

   # The core blocks are then reused by the handwritten model logic.
   if schedule.execute(0, graph, status, status, params):
       neighbor_mean.execute(0, graph, status, status, params)
       selector.execute(0, graph, status, status, params)
       transition.execute(0, graph, status, status, params)
       clip.execute(0, graph, status, status, params)

   # The remaining objects are kept as reusable configuration handles.
   _ = (seed_value, opinion, drift, observe, alias)
