***********************
Worked Examples
***********************

This chapter gives small end-to-end examples. Each one is intentionally short so you can read it line by line.

SIR
===

.. code-block:: ndql

   MODEL SIRExample

   STATUS Susceptible
   STATUS Infected
   STATUS Recovered

   COMPARTMENT infection
   TYPE NodeStochastic
   PARAM rate 0.1
   TRIGGER Infected

   COMPARTMENT recovery
   TYPE NodeStochastic
   PARAM rate 0.05

   RULE
   FROM Susceptible
   TO Infected
   USING infection

   RULE
   FROM Infected
   TO Recovered
   USING recovery

   INITIALIZE
   SET Susceptible 0.95
   SET Infected 0.05
   SET Recovered 0.0

SEIR
====

.. code-block:: ndql

   MODEL SEIRExample

   STATUS Susceptible
   STATUS Exposed
   STATUS Infected
   STATUS Recovered

   COMPARTMENT exposure
   TYPE ExposureRate
   PARAM beta 0.2

   COMPARTMENT latency
   TYPE LatencyPeriod
   PARAM duration 2

   COMPARTMENT recovery
   TYPE RecoveryKernel
   PARAM gamma 0.1

   RULE
   FROM Susceptible
   TO Exposed
   USING exposure

   RULE
   FROM Exposed
   TO Infected
   USING latency

   RULE
   FROM Infected
   TO Recovered
   USING recovery

Algorithmic bias
================

.. code-block:: ndql

   MODEL AlgorithmicBiasExample
   TYPE CONTINUOUS_OPINION
   INITIAL_OPINION_DISTRIBUTION bimodal

   BIN LowOpinion
   BIN HighOpinion

   BLOCK bounded_confidence
   TYPE OpinionDistanceThreshold
   PARAM epsilon 0.15

   BLOCK selection_bias
   TYPE OpinionSelectionBias
   PARAM gamma 1.5

   BLOCK compromise
   TYPE OpinionCompromise
   PARAM mu 0.4

   BLOCK normalization
   TYPE OpinionNormalization
   PARAM min 0.0
   PARAM max 1.0

Voter with zealots
==================

.. code-block:: ndql

   MODEL VoterZealotExample
   TYPE DISCRETE_OPINION

   STATUS Agree
   STATUS Disagree
   STATUS Zealot

   BLOCK seed_nodes
   TYPE SeedSelection
   PARAM share 0.1
   PARAM target seed_nodes

   BLOCK zealot_role
   TYPE NodeRoleAssignment
   PARAM role zealot
   PARAM share 0.1

   INITIALIZE
   SET Agree 0.45
   SET Disagree 0.45
   SET Zealot 0.10

Coupled example
===============

.. code-block:: ndql

   MODEL CoupledExample
   TYPE COUPLED

   STATUS Susceptible
   STATUS Infected
   STATUS Recovered
   BIN LowOpinion
   BIN HighOpinion

   BLOCK opinion_to_infection
   TYPE OpinionAffectsInfection
   PARAM threshold 0.6
   PARAM strength 0.4

   BLOCK infection_feedback
   TYPE InfectionAffectsOpinion
   PARAM source_statuses [Infected]
   PARAM target 0.5
   PARAM strength 0.4

   INITIALIZE
   SET Susceptible 0.90
   SET Infected 0.10
   SET Recovered 0.0
   SET INITIAL_OPINION_DISTRIBUTION uniform

Reading the examples
====================

Notice the pattern:

* names come first
* states are declared explicitly
* blocks are given readable aliases
* parameters are small and local
* initialization is separated from transition logic

That is the style the builder tries to generate automatically.
