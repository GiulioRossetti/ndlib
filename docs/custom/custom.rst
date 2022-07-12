***********************
Custom Model Definition
***********************

``NDlib`` exposes a set of built-in diffusion models (epidemic/opinion dynamics/dynamic network): how can I describe novel ones?

In order to answer such question we developed a syntax for compositional model definition.

=========
Rationale
=========

At a higher level of abstraction a diffusion process can be synthesized into two components:

- Available Statuses, and
- Transition Rules that connect them

All models of ``NDlib`` assume an agent-based, discrete time, simulation engine.
During each simulation iteration all the nodes in the network are asked to (i) evaluate their current status and to (ii) (eventually) apply a matching transition rule.
The last step of such process can be easily decomposed into atomic operations that we will call *compartments*.

.. note::

    ``NDlib`` exposes three classes for defining custom diffusion models:

	- ``CompositeModel`` describes diffusion models for static networks

	- ``DynamicCompositeModel`` describes diffusion models for dynamic networks

	- ``ContinuousModel`` describes diffusion models with continuous states for static and dynamic networks

    To avoid redundant documentation, here we will discuss only the former class, the second behaving alike. The ``ContinuousModel`` class will have a seperate section due to its extra complexity.

============
Compartments
============

We adopt the concept of ``compartment`` to identify all those atomic conditions (i.e. operations) that describe (part of) a transition rule.
The execution of a ``compartment`` can return either *True* (condition satisfied) or *False* (condition not satisfied).

Indeed, several compartments can be described, each one of them capturing an atomic operation.

To cover the main scenarios we defined three families of compartments as well as some operations to combine them.

-----------------
Node Compartments
-----------------

In this class fall all those compartments that evaluate conditions tied to **node** status/features.
They model stochastic events as well as deterministic ones.

.. toctree::
   :maxdepth: 1

   compartments/NodeStochastic.rst
   compartments/NodeCategoricalAttribute.rst
   compartments/NodeNumericalAttribute.rst
   compartments/NodeNumericalVariable.rst
   compartments/NodeThreshold.rst

-----------------
Edge Compartments
-----------------


In this class fall all those compartments that evaluate conditions tied to **edge** features.
They model stochastic events as well as deterministic ones.

.. toctree::
   :maxdepth: 1

   compartments/EdgeStochastic.rst
   compartments/EdgeCategoricalAttribute.rst
   compartments/EdgeNumericalAttribute.rst

-----------------
Time Compartments
-----------------


In this class fall all those compartments that evaluate conditions tied to **temporal execution**.
They can be used to model, for instance, lagged events as well as triggered transitions.

.. toctree::
   :maxdepth: 1

   compartments/CountDown.rst


========================
Compartments Composition
========================

Compartment can be chained in multiple ways so to describe complex transition rules.
In particular, a transition rule can be seen as a tree whose nodes are compartments and edges connections among them.

- The initial node status is evaluated at the root of the tree (the *master* compartment)
- if the operation described by such compartment is satisfied the conditions of (one of) its child compartments is evaluated
- if a path from the root to one leaf of the tree is completely satisfied the transition rule applies and the node change its status.

Compartments can be combined following two criteria:

.. toctree::
   :maxdepth: 1

   compartments/CascadingComposition.rst
   compartments/ConditionalComposition.rst

A rule can be defined by employing all possible combinations of cascading and conditional compartment composition.

========
Examples
========

Here some example of models implemented using compartments.

---
SIR
---

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.CompositeModel as gc
    import ndlib.models.compartments as cpm

    # Network generation
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Composite Model instantiation
    model = gc.CompositeModel(g)

    # Model statuses
    model.add_status("Susceptible")
    model.add_status("Infected")
    model.add_status("Removed")

    # Compartment definition
    c1 = cpm.NodeStochastic(0.02, triggering_status="Infected")
    c2 = cpm.NodeStochastic(0.01)

    # Rule definition
    model.add_rule("Susceptible", "Infected", c1)
    model.add_rule("Infected", "Removed", c2)

    # Model initial status configuration
    config = mc.Configuration()
    config.add_model_parameter('fraction_infected', 0.1)

    # Simulation execution
    model.set_initial_status(config)
    iterations = model.iteration_bunch(5)


For other examples, give a look to the following list of CustomModels:


.. toctree::
   :maxdepth: 1

   compartments/Halloween2021.rst



=======================
Using continuous states
=======================

The composite model only supports discrete states, but more advanced custom models might require continuous states and more options.
If continuous states are required, it might be better to use the continous model implementation.

.. toctree::
   :maxdepth: 2

   continuous_model/continuous_model.rst