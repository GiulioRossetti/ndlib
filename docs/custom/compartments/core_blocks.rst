****************
Core Blocks
****************

The classes in this page are the general-purpose Python blocks used when
assembling custom models programmatically. They live in
``ndlib.models.compartments.NDQLBlocks`` and can be imported directly in a
Python custom-model pipeline.

The examples below focus on the constructor call you use in Python. In a custom
model, these blocks are typically stored as attributes, passed to rules, or used
to generate reusable pieces of a transition tree.

Parameter
=========

Creates a named model parameter.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import Parameter

   beta = Parameter(name="beta", value=0.1, type="float", scope="model")

Constant
=========

Creates a constant value that does not change during the simulation.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import Constant

   seed = Constant(name="seed", value=42, type="int")

Variable
=========

Declares a variable that can live on nodes, edges, or the graph.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import Variable

   opinion = Variable(name="opinion", scope="node", type="continuous", range=[0, 1], default=0.5)

Distribution
============

Describes how to sample bounded initial values.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import Distribution

   init_opinion = Distribution(family="bimodal", bounds=[0, 1], params={"left": 0.2, "right": 0.8})

Selector
========

Selects nodes or neighbors according to a policy.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import Selector

   seeds = Selector(policy="random", share=0.05)

Filter
======

Filters a candidate set using a predicate or expression.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import Filter

   high_opinion = Filter(predicate="opinion > 0.7")

Aggregator
==========

Aggregates values from neighbors or from a selected subset.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import Aggregator

   mean_neighbor_opinion = Aggregator(mode="mean", variable="opinion", target="neighbor_mean")

Kernel
======

Represents a probabilistic kernel used in update logic.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import Kernel

   transmission_kernel = Kernel(rate=0.1, clamp=True)

Transform
=========

Applies a deterministic expression to a value.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import Transform

   relax = Transform(expression="opinion + 0.1", target="opinion")

Compose
=======

Combines blocks into a conditional branch.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import Compose, Filter, Selector

   guard = Filter(predicate="opinion > 0.7")
   branch_true = Selector(policy="random", share=0.05)
   branch_false = Selector(policy="random", share=0.01)
   update = Compose(condition=guard, if_true=branch_true, if_false=branch_false)

Schedule
========

Limits when a block is active.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import Schedule

   school_hours = Schedule(start=8, end=16, period=24, phase=0)

Observe
=======

Describes an observable that can be exported or visualized.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import Observe

   opinion_bins = Observe(variable="opinion", mode="bins", bins=20, range=[0, 1])

ClampNormalize
==============

Clamps or renormalizes a variable into a target interval.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import ClampNormalize

   clip_opinion = ClampNormalize(min=0.0, max=1.0, renormalize=False, target="opinion")

Typical usage pattern
=====================

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import Parameter, Variable, Distribution

   beta = Parameter(name="beta", value=0.1, type="float")
   opinion = Variable(name="opinion", scope="node", type="continuous", range=[0, 1], default=0.5)
   init_opinion = Distribution(family="uniform", bounds=[0, 1])

   # These objects are then combined by the custom model code that builds
   # transition rules and initialization logic.
