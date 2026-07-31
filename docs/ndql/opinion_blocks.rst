************************
Opinion Blocks
************************

Opinion blocks are the core of continuous and discrete opinion models. They define how node opinions are initialized, updated, normalized, and constrained.

OpinionDistribution
===================

Samples bounded starting opinions from a named distribution.

Example:

.. code-block:: ndql

   BLOCK opinion_distribution
   TYPE OpinionDistribution
   PARAM family bimodal
   PARAM bounds [0,1]

OpinionDistanceThreshold
========================

Implements bounded confidence through an ``epsilon`` threshold.

Example:

.. code-block:: ndql

   BLOCK bounded_confidence
   TYPE OpinionDistanceThreshold
   PARAM epsilon 0.2

OpinionSelectionBias
====================

Biases partner selection by opinion distance.

Example:

.. code-block:: ndql

   BLOCK selection_bias
   TYPE OpinionSelectionBias
   PARAM gamma 1.5

OpinionCompromise
=================

Applies Deffuant-style averaging.

Example:

.. code-block:: ndql

   BLOCK compromise
   TYPE OpinionCompromise
   PARAM mu 0.5

OpinionStubbornness
===================

Reduces the amount of opinion movement.

Example:

.. code-block:: ndql

   BLOCK stubbornness
   TYPE OpinionStubbornness
   PARAM theta 0.1

OpinionNoise
============

Adds bounded stochastic perturbation to the opinion.

Example:

.. code-block:: ndql

   BLOCK noise
   TYPE OpinionNoise
   PARAM sigma 0.02

OpinionPolarization
===================

Pushes opinions toward extreme values.

Example:

.. code-block:: ndql

   BLOCK polarization
   TYPE OpinionPolarization
   PARAM strength 0.3

OpinionExternalField
====================

Pulls opinions toward a target value.

Example:

.. code-block:: ndql

   BLOCK external_field
   TYPE OpinionExternalField
   PARAM target 0.8
   PARAM strength 0.2

OpinionTrustFilter
==================

Restricts influence to trusted opinion ranges.

Example:

.. code-block:: ndql

   BLOCK trust_filter
   TYPE OpinionTrustFilter
   PARAM trust_threshold 0.15

OpinionConsensusBlock
=====================

Combines opinions into a shared consensus update.

Example:

.. code-block:: ndql

   BLOCK consensus
   TYPE OpinionConsensusBlock
   PARAM mode mean
   PARAM confidence 0.6

OpinionRepulsion
================

Pushes opinions away from dissimilar neighbors.

Example:

.. code-block:: ndql

   BLOCK repulsion
   TYPE OpinionRepulsion
   PARAM epsilon 0.1
   PARAM strength 0.2

OpinionAssimilation
===================

Blends neighbor opinions through a simple assimilation rate.

Example:

.. code-block:: ndql

   BLOCK assimilation
   TYPE OpinionAssimilation
   PARAM rate 0.3

OpinionMemory
=============

Retains part of the past opinion state.

Example:

.. code-block:: ndql

   BLOCK memory
   TYPE OpinionMemory
   PARAM alpha 0.5

OpinionNormalization
====================

Clamps or rescales opinions into a target interval.

Example:

.. code-block:: ndql

   BLOCK normalization
   TYPE OpinionNormalization
   PARAM min 0.0
   PARAM max 1.0

OpinionQuantization
===================

Rounds continuous opinions into bins.

Example:

.. code-block:: ndql

   BLOCK quantization
   TYPE OpinionQuantization
   PARAM bins 10

OpinionMediaInfluence
=====================

Mixes node opinions with one or more media opinions.

Example:

.. code-block:: ndql

   BLOCK media
   TYPE OpinionMediaInfluence
   PARAM k 2
   PARAM media_opinions [0.2,0.8]
   PARAM weight 0.25

OpinionZealot
=============

Makes a fraction of nodes immutable or fixed to a target value.

Example:

.. code-block:: ndql

   BLOCK zealot
   TYPE OpinionZealot
   PARAM share 0.1
   PARAM fixed_value 1.0

OpinionMultiTopic
=================

Represents multiple coupled opinion topics.

Example:

.. code-block:: ndql

   BLOCK multi_topic
   TYPE OpinionMultiTopic
   PARAM topics [economy,health]
   PARAM coupling 0.2

OpinionLabelSwitch
==================

Switches between opinion labels or symbolic states.

Example:

.. code-block:: ndql

   BLOCK label_switch
   TYPE OpinionLabelSwitch
   PARAM labels [A,B]
   PARAM probability 0.25

OpinionBoundedDrift
===================

Moves opinions by a bounded deterministic step.

Example:

.. code-block:: ndql

   BLOCK bounded_drift
   TYPE OpinionBoundedDrift
   PARAM step 0.1
   PARAM bounds [0,1]
