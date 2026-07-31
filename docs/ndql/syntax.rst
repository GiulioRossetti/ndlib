********************
NDQL Syntax
********************

NDQL is intentionally line-oriented. That makes scripts easy to scan, easy to generate, and easy to round-trip.

General rules
=============

* One directive per line.
* Identifiers are case-sensitive in the model text.
* Comments begin with ``#``.
* Spaces separate directive keywords and parameters.
* Lists are written in bracket notation, for example ``[0,1]``.
* The language keeps backward compatibility with older epidemic scripts while allowing richer typed declarations for builder-generated models.

The most important directive families are:

* model header directives
* declarations
* state declarations
* blocks and compartments
* rules and compositions
* initialization directives
* network directives
* execution directives
* observables and update directives

Model header
============

.. code-block:: ndql

   MODEL MyModel
   TYPE EPIDEMIC

``TYPE`` is recommended when the model family is known explicitly. The dashboard uses it to distinguish epidemic, opinion, and coupled workflows.

Declarations
============

Use ``DECLARE`` to introduce typed values:

.. code-block:: ndql

   DECLARE PARAM beta TYPE float DEFAULT 0.1
   DECLARE PARAM gamma TYPE float DEFAULT 0.05
   DECLARE VARIABLE opinion TYPE continuous RANGE [0,1] DEFAULT 0.5
   DECLARE GLOBAL run_name TYPE string DEFAULT DemoRun

Common kinds are:

* ``PARAM`` for model parameters
* ``GLOBAL`` for shared model-wide metadata
* ``VARIABLE`` for node, edge, or graph state
* ``EDGE_VARIABLE`` when edge state is needed
* ``STATUS`` and ``BIN`` for compatibility-oriented state declarations

State declarations
==================

Use ``STATUS`` for epidemic or discrete-opinion states:

.. code-block:: ndql

   STATUS Susceptible
   STATUS Infected
   STATUS Recovered

Use ``BIN`` for continuous-opinion labels in the current builder output:

.. code-block:: ndql

   BIN LowOpinion
   BIN HighOpinion

Blocks and compartments
=======================

The two common forms are:

.. code-block:: ndql

   COMPARTMENT infection
   TYPE NodeStochastic
   PARAM rate 0.1

and:

.. code-block:: ndql

   BLOCK bounded_confidence
   TYPE OpinionDistanceThreshold
   PARAM epsilon 0.2

The builder may emit either name depending on the family and the underlying block.

Rules and compositions
======================

Classic transitions are written as rules:

.. code-block:: ndql

   RULE
   FROM Susceptible
   TO Infected
   USING infection

Composition blocks can be written explicitly:

.. code-block:: ndql

   IF guard THEN branch_a ELSE branch_b AS combined_rule

Initialization
==============

Initialization declares the starting state of the model:

.. code-block:: ndql

   INITIALIZE
   SET Susceptible 0.95
   SET Infected 0.05
   SET INITIAL_OPINION_DISTRIBUTION bimodal

Network directives
==================

NDQL can describe how a network is created or loaded:

.. code-block:: ndql

   CREATE_NETWORK g1
   TYPE erdos_renyi_graph
   PARAM n 300
   PARAM p 0.1

   LOAD_NETWORK g2 FROM graph.graphml

Execution
=========

Running a script is explicit:

.. code-block:: ndql

   EXECUTE SIRExample ON g1 FOR 100

Observables and updates
=======================

NDQL can also declare what should be observed and how opinions should be updated:

.. code-block:: ndql

   OBSERVE opinion AS bins BINS 20 RANGE [0,1]
   WHEN iteration >= 10
   SCHEDULE 10 50 PERIOD 1 PHASE 0
   UPDATE opinion = clamp(opinion + mu * (neighbor_mean - opinion), 0, 1)

This is the part of the language that makes builder-generated opinion models readable and explicit.
