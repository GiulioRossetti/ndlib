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

============
Compartments
============

We adopt the concept of ``compartment`` to identify all those atomic conditions (i.e. operations) that describe a (part of) transition rule.
The execution of a ``compartment`` can return either *True* (condition satisfied) or *False* (condition not satisfied).

Consider the transition rule **Susceptible->Infected** that requires a probability *beta* to be satisfied.
Such rule can be described by a simple compartment that models Node Stochastic thresholds. Let's call il *NS*.

*NS* will take as input the *initial* node status (Susceptible), the *final* one (Infected) and a probability threshold (*beta*).

During each iteration, for each node *n*

- if the actual status of a given node equals the *NS* initial one
	- a random value *b* in [0,1] will be generated
	- if *b <= beta* then *NS* is considered *satisfied* and the status of *n* changes from *Susceptible* to *Infected*.

Indeed, several compartments can be described, each one of them capturing an atomic operation.

To cover the main scenarios we defined three families of compartments.

-----------------
Node Compartments
-----------------

In this class fall all those compartments that evaluate conditions tied to **node** status/features.
They model stochastic events as well as deterministic ones.

.. toctree::
   :maxdepth: 2

   compartments/NodeStochastic.rst
   compartments/NodeCategoricalAttribute.rst
   compartments/NodeNumericalAttribute.rst
   compartments/NodeThreshold.rst

-----------------
Edge Compartments
-----------------


In this class fall all those compartments that evaluate conditions tied to **edge** features.
They model stochastic events as well as deterministic ones.

.. toctree::
   :maxdepth: 2

   compartments/EdgeStochastic.rst
   compartments/EdgeCategoricalAttribute.rst
   compartments/EdgeNumericalAttribute.rst

-----------------
Time Compartments
-----------------


In this class fall all those compartments that evaluate conditions tied to **temporal execution**.
They can be used to model, for instance, lagged events as well as triggered transitions.

.. toctree::
   :maxdepth: 2

   compartments/CountDown.rst


=======================
Compartment Composition
=======================

Compartment can be chained in multiple ways so to describe complex transition rules.
In particular, a transition rule can be seen as a tree whose nodes are compartments and edges connections among them.

- The initial node status is evaluated at the root of the tree (the *master* compartment)
- if the operation described by such compartment is satisfied the conditions of (one of) its child compartments is evaluated
- if a path from the root to one leaf of the tree is completely satisfied the transition rule applies and the node change its status.

Compartments can be combined following two criteria:

.. toctree::
   :maxdepth: 2

   compartments/CascadingComposition.rst
   compartments/ConditionalComposition.rst


========
Examples
========

Here some example of models implemented using compartments.