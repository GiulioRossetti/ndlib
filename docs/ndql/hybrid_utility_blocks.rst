*************************
Hybrid and Utility Blocks
*************************

Hybrid blocks connect epidemic and opinion dynamics. Utility blocks help the builder prepare, validate, and preview a model.

Hybrid blocks
=============

AttributeCoupling
-----------------

Couples one attribute to another.

Example:

.. code-block:: ndql

   BLOCK attribute_link
   TYPE AttributeCoupling
   PARAM attribute opinion
   PARAM source infection
   PARAM target recovery
   PARAM strength 0.5

OpinionAffectsInfection
-----------------------

Uses opinion to modulate infection risk.

Example:

.. code-block:: ndql

   BLOCK opinion_to_infection
   TYPE OpinionAffectsInfection
   PARAM threshold 0.6
   PARAM strength 0.4

OpinionAffectsRecovery
----------------------

Uses opinion to modulate recovery.

Example:

.. code-block:: ndql

   BLOCK opinion_to_recovery
   TYPE OpinionAffectsRecovery
   PARAM threshold 0.5
   PARAM strength 0.3

OpinionAffectsContactRate
-------------------------

Uses opinion to modulate contact rate.

Example:

.. code-block:: ndql

   BLOCK opinion_to_contact
   TYPE OpinionAffectsContactRate
   PARAM threshold 0.4
   PARAM strength 0.2

InfectionAffectsOpinion
-----------------------

Lets infection status feed back into opinion updates.

Example:

.. code-block:: ndql

   BLOCK infection_feedback
   TYPE InfectionAffectsOpinion
   PARAM source_statuses [Infected]
   PARAM target 0.5
   PARAM strength 0.4

StatusDependentOpinionUpdate
----------------------------

Selects the opinion update path according to the current status.

Example:

.. code-block:: ndql

   BLOCK status_driven_update
   TYPE StatusDependentOpinionUpdate
   PARAM status_filter Infected
   PARAM target opinion

EpidemicDependentBias
---------------------

Changes opinion-selection bias according to epidemic status.

Example:

.. code-block:: ndql

   BLOCK epidemic_bias
   TYPE EpidemicDependentBias
   PARAM status_filter Infected
   PARAM status_weight 0.7

PolicyIntervention
------------------

Represents a policy action applied during a time window.

Example:

.. code-block:: ndql

   BLOCK lockdown
   TYPE PolicyIntervention
   PARAM start 10
   PARAM end 20
   PARAM action scale
   PARAM value 0.5

CommunityCoupling
-----------------

Couples a block to community membership.

Example:

.. code-block:: ndql

   BLOCK community_coupling
   TYPE CommunityCoupling
   PARAM community_field com
   PARAM intra 1.0
   PARAM inter 0.5

Utility blocks
==============

SeedSelection
-------------

Selects the initial seed nodes for epidemic or zealot workflows.

Example:

.. code-block:: ndql

   BLOCK seed_nodes
   TYPE SeedSelection
   PARAM share 0.05
   PARAM target seed_nodes

NodeRoleAssignment
------------------

Assigns a role such as ``seed`` or ``zealot`` to selected nodes.

Example:

.. code-block:: ndql

   BLOCK role_assignment
   TYPE NodeRoleAssignment
   PARAM role seed
   PARAM share 0.1

AttributeInitializer
--------------------

Initializes a node, edge, or graph attribute from a distribution or literal.

Example:

.. code-block:: ndql

   BLOCK opinion_initializer
   TYPE AttributeInitializer
   PARAM attribute opinion
   PARAM distribution uniform
   PARAM scope node

GraphImport
-----------

Imports graph-level metadata or merges a graph payload into the current model.

Example:

.. code-block:: ndql

   BLOCK graph_import
   TYPE GraphImport
   PARAM merge true
   PARAM scope graph

CommunityAssignment
-------------------

Computes community labels and stores them in a node field.

Example:

.. code-block:: ndql

   BLOCK community_assignment
   TYPE CommunityAssignment
   PARAM algorithm louvain_communities
   PARAM field com

RuleAlias
---------

Gives a readable alias to a rule or a parameterized pattern.

Example:

.. code-block:: ndql

   BLOCK rule_alias
   TYPE RuleAlias
   PARAM alias infection_step
   PARAM target infection_transition

PreviewObservable
-----------------

Requests a preview-friendly observable configuration.

Example:

.. code-block:: ndql

   BLOCK preview_opinion
   TYPE PreviewObservable
   PARAM variable opinion
   PARAM mode bins
   PARAM bins 20

ValidationHint
--------------

Carries validator-friendly metadata for the builder or parser.

Example:

.. code-block:: ndql

   BLOCK opinion_range
   TYPE ValidationHint
   PARAM name opinion_range
   PARAM minimum 0.0
   PARAM maximum 1.0
