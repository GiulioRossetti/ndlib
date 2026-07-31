****************
Core Blocks
****************

Core blocks are the building blocks used across epidemic, opinion, and coupled models.

Parameter
=========

Declares a typed model parameter.

Example:

.. code-block:: ndql

   DECLARE PARAM beta TYPE float DEFAULT 0.1

Constant
========

Declares an immutable value.

Example:

.. code-block:: ndql

   DECLARE CONSTANT run_id TYPE string DEFAULT baseline

Variable
========

Declares a variable that can live on nodes, edges, or the graph.

Example:

.. code-block:: ndql

   DECLARE VARIABLE opinion TYPE continuous RANGE [0,1] DEFAULT 0.5

Distribution
============

Describes how bounded values should be sampled.

Example:

.. code-block:: ndql

   BLOCK init_opinion TYPE Distribution
   PARAM family bimodal
   PARAM bounds [0,1]

Selector
========

Chooses nodes or neighbors according to a policy.

Example:

.. code-block:: ndql

   BLOCK pick_seed TYPE Selector
   PARAM policy random
   PARAM share 0.05

Filter
======

Filters a node set through a predicate or expression.

Example:

.. code-block:: ndql

   BLOCK high_opinion_only TYPE Filter
   PARAM predicate opinion > 0.7

Aggregator
==========

Aggregates values from a neighborhood or a selected set.

Example:

.. code-block:: ndql

   BLOCK mean_neighbor_opinion TYPE Aggregator
   PARAM mode mean
   PARAM variable opinion

Kernel
======

Encodes a probabilistic update kernel.

Example:

.. code-block:: ndql

   BLOCK transmission_kernel TYPE Kernel
   PARAM rate 0.1

Transform
=========

Applies a deterministic expression to a value.

Example:

.. code-block:: ndql

   BLOCK relax TYPE Transform
   PARAM expression opinion + 0.1

Compose
=======

Combines two or more blocks into a conditional workflow.

Example:

.. code-block:: ndql

   BLOCK update_rule TYPE Compose
   PARAM condition guard
   PARAM if_true spread
   PARAM if_false stay

Schedule
========

Limits execution to a time window or periodic schedule.

Example:

.. code-block:: ndql

   BLOCK school_hours TYPE Schedule
   PARAM start 8
   PARAM end 16
   PARAM period 24

Observe
=======

Declares an observable for export or plotting.

Example:

.. code-block:: ndql

   OBSERVE opinion AS bins BINS 20 RANGE [0,1]

ClampNormalize
==============

Constrains a variable into a target interval.

Example:

.. code-block:: ndql

   BLOCK clip_opinion TYPE ClampNormalize
   PARAM min 0
   PARAM max 1
