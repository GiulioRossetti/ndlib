*************************
Hybrid and Utility Blocks
*************************

The classes in this page help bridge epidemic and opinion dynamics or support
model assembly, initialization, validation, and preview behavior. They are
imported from ``ndlib.models.compartments.NDQLBlocks`` and are meant to be used
directly in Python custom-model pipelines.

AttributeCoupling
============================

Links a node attribute to another variable with a tunable strength.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import AttributeCoupling

   coupling = AttributeCoupling(attribute="risk", source="opinion", target="contact_rate", strength=0.4)

OpinionAffectsInfection
============================

Uses opinion values to modulate infection risk.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionAffectsInfection

   bias = OpinionAffectsInfection(threshold=0.5, strength=0.3, invert=False)

OpinionAffectsRecovery
============================

Uses opinion values to modulate recovery behavior.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionAffectsRecovery

   recovery_bias = OpinionAffectsRecovery(threshold=0.6, strength=0.2, invert=False)

OpinionAffectsContactRate
============================

Adjusts contact intensity according to the current opinion.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionAffectsContactRate

   contact_bias = OpinionAffectsContactRate(threshold=0.4, strength=0.5)

InfectionAffectsOpinion
============================

Shifts opinions after infection events or based on infection status.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import InfectionAffectsOpinion

   response = InfectionAffectsOpinion(source_statuses=["Infected"], target=0.2, strength=0.4)

StatusDependentOpinionUpdate
============================

Applies different opinion-update kernels depending on the epidemic status.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import StatusDependentOpinionUpdate

   update = StatusDependentOpinionUpdate(status_filter=["Infected"], strength=0.5, fallback=0.1)

EpidemicDependentBias
============================

Computes selection bias from the current epidemic status mix.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import EpidemicDependentBias

   bias = EpidemicDependentBias(status_filter=["Infected"], status_weight=0.7)

PolicyIntervention
============================

Scales or overrides a target quantity within a time window.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import PolicyIntervention

   lockdown = PolicyIntervention(start=10, end=30, action="scale", value=0.5, target="contact_rate")

CommunityCoupling
============================

Controls interaction strength within and across communities.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import CommunityCoupling

   coupling = CommunityCoupling(community_field="com", intra=1.0, inter=0.3, target="opinion")

SeedSelection
============================

Chooses the nodes to initialize a simulation seed set.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import SeedSelection

   seeds = SeedSelection(share=0.05, target="seed_nodes")

NodeRoleAssignment
============================

Assigns semantic roles to nodes, such as seed, hub, or influencer.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import NodeRoleAssignment

   roles = NodeRoleAssignment(role="seed", share=0.1, target="role")

AttributeInitializer
============================

Initializes node, edge, or graph attributes before the simulation starts.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import AttributeInitializer

   init = AttributeInitializer(attribute="opinion", distribution="uniform", scope="node")

GraphImport
============================

Loads a graph payload or merges a graph structure into the model state.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import GraphImport

   graph_import = GraphImport(source="graphml", merge=True)

CommunityAssignment
============================

Builds or stores community memberships for later use in blocks.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import CommunityAssignment

   communities = CommunityAssignment(algorithm="louvain_communities", field="com")

RuleAlias
============================

Provides an alias for a reusable rule or block chain.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import RuleAlias

   alias = RuleAlias(alias="high_risk_policy", description="Cap contacts during outbreaks")

PreviewObservable
============================

Declares a value that should be exported for inspection or plotting.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import PreviewObservable

   preview = PreviewObservable(variable="opinion", mode="bins", bins=20, range=[0, 1])

ValidationHint
============================

Attaches range or consistency hints to a block parameter.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import ValidationHint

   hint = ValidationHint(name="coverage", minimum=0.0, maximum=1.0, message="Coverage must stay in [0, 1]")

Typical usage pattern
============================

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import (
       AttributeInitializer,
       CommunityCoupling,
       PolicyIntervention,
       PreviewObservable,
   )

   init_opinion = AttributeInitializer(attribute="opinion", distribution="bimodal", scope="node")
   community_bias = CommunityCoupling(community_field="com", intra=1.0, inter=0.4)
   intervention = PolicyIntervention(start=15, end=30, action="scale", value=0.7, target="contact_rate")
   observed_opinion = PreviewObservable(variable="opinion", mode="bins", bins=25, range=[0, 1])

   # These blocks are then combined by the custom-model code to initialize
   # attributes, couple epidemic/opinion behavior, and expose observables.
