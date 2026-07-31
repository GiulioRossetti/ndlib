**********************
Hybrid Model Example
**********************

This example combines the hybrid blocks with the utility blocks so the same
graph carries both epidemic status and opinion metadata. The blocks are applied
directly to the nodes, which matches the execution pattern used by the current
dashboard tests.

.. code-block:: python

   import networkx as nx

   from ndlib.models.compartments.NDQLBlocks import (
       AttributeCoupling,
       AttributeInitializer,
       CommunityAssignment,
       CommunityCoupling,
       EpidemicDependentBias,
       InfectionAffectsOpinion,
       NodeRoleAssignment,
       OpinionAffectsContactRate,
       OpinionAffectsInfection,
       OpinionAffectsRecovery,
       PolicyIntervention,
       PreviewObservable,
       RuleAlias,
       SeedSelection,
       StatusDependentOpinionUpdate,
       ValidationHint,
   )

   graph = nx.barabasi_albert_graph(20, 2, seed=11)
   for node in graph.nodes():
       graph.nodes[node]["com"] = 0 if node < 10 else 1
       graph.nodes[node]["opinion"] = 0.2 + 0.6 * (node % 2)

   status = {node: 0 for node in graph.nodes()}
   status[0] = 1
   status[9] = 1
   params = {"model": {"iteration": 0, "available_statuses": {"Susceptible": 0, "Infected": 1}}}

   seed = SeedSelection(nodes=[0, 9], target="seed_nodes")
   role = NodeRoleAssignment(role="zealot", nodes=[0, 9], target="role")
   attrs = AttributeInitializer(attribute="opinion", value=0.5, scope="node")
   communities = CommunityAssignment(
       community_map={node: graph.nodes[node]["com"] for node in graph.nodes()},
       field="community",
       target="com",
   )
   contact_bias = OpinionAffectsContactRate(threshold=0.5, strength=0.5, target="contact_rate")
   infection_bias = OpinionAffectsInfection(threshold=0.5, strength=0.4, target="infection_risk")
   recovery_bias = OpinionAffectsRecovery(threshold=0.5, strength=0.2, target="recovery_rate")
   coupling = AttributeCoupling(attribute="opinion", source="opinion", target="contact_rate", strength=0.5)
   infect_to_opinion = InfectionAffectsOpinion(source_statuses=[1], target=0.1, strength=0.4)
   status_update = StatusDependentOpinionUpdate(status_filter=[1], kernel="neighbor_mean", strength=0.2, fallback=0.5)
   epi_bias = EpidemicDependentBias(status_filter=[1], status_weight=0.8, cross_status_factor=0.2)
   community = CommunityCoupling(community_field="com", intra=1.0, inter=0.25, target="opinion")
   policy = PolicyIntervention(start=10, end=20, target="contact_rate", action="scale", value=0.6)
   preview = PreviewObservable(variable="opinion", mode="bins", bins=15, range=[0, 1])
   hint = ValidationHint(name="opinion", minimum=0.0, maximum=1.0, target="opinion")
   alias = RuleAlias(alias="hybrid_feedback", target="opinion", description="Couple epidemic and opinion feedback")

   seed.execute(0, graph, status, status, params)
   role.execute(0, graph, status, status, params)
   attrs.execute(0, graph, status, status, params)
   communities.execute(0, graph, status, status, params)

   for node in graph.nodes():
       contact_bias.execute(node, graph, status, status, params)
       infection_bias.execute(node, graph, status, status, params)
       recovery_bias.execute(node, graph, status, status, params)
       coupling.execute(node, graph, status, status, params)
       infect_to_opinion.execute(node, graph, status, status, params)
       status_update.execute(node, graph, status, status, params)
       epi_bias.execute(node, graph, status, status, params)
       community.execute(node, graph, status, status, params)
       policy.execute(node, graph, status, status, params)
       preview.execute(node, graph, status, status, params)
       hint.execute(node, graph, status, status, params)

   _ = alias
