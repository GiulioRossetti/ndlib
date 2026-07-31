******************
Opinion Blocks
******************

The classes in this page are the Python opinion blocks used to build continuous
and discrete opinion models directly in code. They are imported from
``ndlib.models.compartments.NDQLBlocks``.

OpinionDistribution
===================

Samples initial opinions from a chosen family.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionDistribution

   initial_opinions = OpinionDistribution(family="uniform", bounds=[0, 1])

OpinionStubbornness
===================

Adds inertia to opinion updates.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionStubbornness

   stubbornness = OpinionStubbornness(theta=0.2, floor=0.0)

OpinionNoise
============

Adds stochastic perturbation to an opinion update.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionNoise

   noise = OpinionNoise(sigma=0.05, distribution="gaussian")

OpinionPolarization
===================

Pushes opinions toward the extremes.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionPolarization

   polarization = OpinionPolarization(strength=0.2, attractor_points=[0.0, 1.0])

OpinionMediaInfluence
=====================

Mixes node opinions with one or more media opinions.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionMediaInfluence

   media = OpinionMediaInfluence(k=2, media_opinions=[0.2, 0.8], weights=[0.6, 0.4])

OpinionTrustFilter
==================

Keeps only influences that pass a trust threshold.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionTrustFilter

   trust = OpinionTrustFilter(trust_threshold=0.3, signed=False)

OpinionConsensusBlock
=====================

Aggregates opinions into a shared consensus update.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionConsensusBlock

   consensus = OpinionConsensusBlock(mode="mean", confidence=0.2, target="opinion")

OpinionRepulsion
================

Moves opinions away from sufficiently different neighbors.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionRepulsion

   repulsion = OpinionRepulsion(epsilon=0.1, strength=0.2)

OpinionAssimilation
===================

Blends opinions with a simple assimilation rate.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionAssimilation

   assimilation = OpinionAssimilation(rate=0.4)

OpinionExternalField
====================

Pulls opinions toward an external target value.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionExternalField

   external_field = OpinionExternalField(target=0.6, strength=0.2)

OpinionMultiTopic
=================

Represents multiple coupled opinion topics.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionMultiTopic

   mult_topic = OpinionMultiTopic(topics=["economy", "health"], coupling=0.3)

OpinionLabelSwitch
==================

Handles symbolic opinion-label transitions.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionLabelSwitch

   label_switch = OpinionLabelSwitch(labels=["A", "B"], probability=0.5)

OpinionBoundedDrift
===================

Moves an opinion in bounded deterministic steps.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionBoundedDrift

   drift = OpinionBoundedDrift(step=0.1, bounds=[0, 1], noise=0.0)

Typical usage pattern
=====================

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import OpinionDistribution, OpinionNoise, OpinionAssimilation

   init = OpinionDistribution(family="bimodal", bounds=[0, 1])
   jitter = OpinionNoise(sigma=0.03)
   update = OpinionAssimilation(rate=0.5)

   # These blocks are combined by the opinion custom model code to define the
   # initialization and update rules.
