*******************************
Builder to NDQL Mapping
*******************************

The dashboard builder is not a separate system. It is a structured editor for NDQL and for the Python custom-model generator that sits behind it.

How the builder maps to NDQL
============================

* Status cards become ``STATUS`` or ``BIN`` declarations.
* The initial status panel becomes the ``INITIALIZE`` section.
* Compartments and blocks become ``COMPARTMENT`` or ``BLOCK`` sections.
* Edges between cards become ``RULE`` connections or composition links.
* The NDQL preview is the direct textual representation of the current canvas.
* Saving the model writes both the textual NDQL and the generated Python source.

Epidemic workflows
==================

When you select an epidemic model in the builder:

* the status ratio panel appears
* seed-node selection is enabled on the preview graph
* the graph can show community-aware layouts when communities are available
* the preview remains interactive for selecting initial infected nodes

Example mapping:

.. code-block:: ndql

   STATUS Susceptible
   STATUS Infected
   STATUS Recovered

   COMPARTMENT infection
   TYPE NodeStochastic
   PARAM rate 0.1

   RULE
   FROM Susceptible
   TO Infected
   USING infection

Continuous-opinion workflows
============================

For continuous-opinion models, the builder also exposes:

* an initial opinion distribution dropdown
* continuous-opinion blocks such as bounded confidence, selection bias, compromise, and normalization
* a binned opinion distribution chart in the network view

Example mapping:

.. code-block:: ndql

   TYPE CONTINUOUS_OPINION
   INITIAL_OPINION_DISTRIBUTION bimodal

   BIN LowOpinion
   BIN HighOpinion

   BLOCK bounded_confidence
   TYPE OpinionDistanceThreshold
   PARAM epsilon 0.2

Discrete-opinion workflows
==========================

For discrete-opinion models, the builder exposes class percentages instead of a single infected share.

Example mapping:

.. code-block:: ndql

   STATUS Agree
   STATUS Disagree
   STATUS Zealot

   INITIALIZE
   SET Agree 0.45
   SET Disagree 0.45
   SET Zealot 0.10

Coupled workflows
==================

Coupled models can mix epidemic and opinion blocks in the same canvas.

The builder keeps the palette synchronized with the active family so the NDQL preview, the inspector, and the generated Python model describe the same behavior.

Practical advice
================

* Use the builder when you want to compose the model visually.
* Use the NDQL preview when you want to audit the generated text.
* Use the NDQL manual when you need to understand the meaning of a directive or block.
