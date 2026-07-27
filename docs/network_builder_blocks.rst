****************************************
Network Builder Blocks and NDQL Guide
****************************************

This guide documents the block vocabulary exposed by the visual network builder and the NDQL emitted by the builder.

The current implementation is intentionally pragmatic:

* epidemic blocks remain status-transition oriented
* continuous opinion blocks support bounded confidence, biased partner selection, compromise, and optional opinion post-processing
* discrete opinion models use percentage-based initial class assignment
* opinion-oriented dashboards expose continuous initial opinion distributions in the simulation controls

Builder workflow
=================

1. Choose the model family in the builder sidebar.
2. Add status nodes for the states in your model.
3. Add compartments from the palette.
4. Connect statuses to compartments and back to statuses.
5. Edit the compartment parameters in the inspector.
6. Save the model to generate Python and NDQL artifacts.

Core builder blocks
===================

Status node
-----------

Declares a model state.

Typical use:

* epidemic compartments such as ``Susceptible`` and ``Infected``
* opinion labels such as ``Agree`` and ``Disagree``

Supported model metadata:

* status name
* numeric code

Node stochastic
---------------

Stochastic neighbor-triggered transition.

Key parameters:

* ``rate``
* ``triggering_status``

Node threshold
--------------

Fraction-based trigger.

Key parameters:

* ``threshold``
* ``triggering_status``

Edge stochastic
---------------

Edge-level stochastic trigger.

Count down
----------

Fixed duration delay block.

Key parameter:

* ``iterations``

Node categorical attribute
--------------------------

Tests a categorical node attribute.

Key parameters:

* ``attribute``
* ``value``
* ``probability``

Node numerical attribute
------------------------

Tests a numerical attribute or range.

Key parameters:

* ``attribute``
* ``op``
* ``value``
* ``probability``

Node numerical variable
-----------------------

Tests a numeric node variable or opinion-like attribute.

Key parameters:

* ``var``
* ``var_type``
* ``value_type``
* ``op``
* ``value``
* ``probability``

Conditional composition
-----------------------

Combines three blocks through an ``IF ... THEN ... ELSE ...`` structure.

Key parameters:

* ``condition``
* ``first_branch``
* ``second_branch``

Continuous opinion blocks
==========================

These blocks are available in the continuous opinion builder palette and are serialized into the custom model pipeline.

Opinion distance threshold
--------------------------

Bounded-confidence gate.

Key parameter:

* ``epsilon``

Opinion selection bias
----------------------

Biases partner selection toward similar opinions.

Key parameter:

* ``gamma``

Opinion compromise
------------------

Performs averaging between interacting opinions.

Key parameter:

* ``mu``

Opinion stubbornness
--------------------

Reduces how much a node moves toward neighbors.

Key parameter:

* ``theta``

Opinion noise
-------------

Adds bounded stochastic perturbation.

Key parameter:

* ``sigma``

Opinion polarization
--------------------

Pushes opinions toward extremes.

Key parameter:

* ``strength``

Opinion external field
----------------------

Pulls opinions toward a global target.

Key parameters:

* ``target``
* ``strength``

Opinion trust filter
--------------------

Limits influence to trusted opinions.

Key parameter:

* ``trust_threshold``

Opinion memory
--------------

Retains past opinions.

Key parameter:

* ``alpha``

Opinion normalization
---------------------

Clamps opinions into a target interval.

Key parameters:

* ``min``
* ``max``

Opinion quantization
--------------------

Rounds continuous opinions to discrete bins.

Key parameter:

* ``bins``

Opinion media influence
-----------------------

Mixes a node opinion with one or more media opinions.

Key parameter:

* ``weight``

Initial opinion distribution
============================

Continuous opinion models expose a global distribution selector in the builder and in the simulation controls.

Supported values:

* ``uniform``
* ``normal`` and ``gaussian``
* ``bimodal``
* ``left_skewed``
* ``right_skewed``
* ``polarized``

NDQL emitted by the builder uses:

.. code-block:: ndql

   TYPE CONTINUOUS_OPINION
   INITIAL_OPINION_DISTRIBUTION bimodal

Example builders
================

Algorithmic bias starter
------------------------

The starter layout combines:

* ``OpinionDistanceThreshold``
* ``OpinionSelectionBias``
* ``OpinionCompromise``

This is the recommended base for bounded-confidence style opinion models.

Mixed advanced starter
----------------------

The coupled starter exposes the same opinion blocks together with epidemic blocks and conditional composition.

Generated NDQL
==============

The builder generates a line-oriented NDQL script.

For continuous opinions, the format is:

.. code-block:: ndql

   MODEL MyModel
   TYPE CONTINUOUS_OPINION
   INITIAL_OPINION_DISTRIBUTION uniform

   BLOCK bounded_confidence
   TYPE OpinionDistanceThreshold
   PARAM epsilon 0.1

   BLOCK selection_bias
   TYPE OpinionSelectionBias
   PARAM gamma 1.5

   BLOCK opinion_compromise
   TYPE OpinionCompromise
   PARAM mu 0.5

The builder also emits opinion-processing blocks such as normalization or quantization when they are present in the canvas.
