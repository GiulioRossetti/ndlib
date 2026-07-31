***************************
Getting Started With NDQL
***************************

NDQL is a small, line-oriented language for describing diffusion models without writing Python code.

It is designed for three kinds of users:

* people who want to read or share a model as text
* people who want to build a model visually and inspect the generated script
* people who want a stable text format that can be parsed, saved, reloaded, and translated into Python

What NDQL describes
===================

NDQL can represent:

* epidemic compartment models
* continuous opinion models
* discrete opinion models
* coupled epidemic-opinion systems
* custom model pipelines built from reusable blocks

The key idea is simple:

* a script names the model
* the script declares statuses, variables, and parameters
* the script defines blocks or compartments
* the script connects those blocks with rules
* the script specifies initialization and execution

A first example
===============

Here is a small epidemic model:

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

The same structure is used by the builder: statuses appear first, then compartments or blocks, then rules, then initialization.

How to read a script
====================

Read NDQL from top to bottom:

* ``MODEL`` gives the model a name
* ``TYPE`` declares the family when needed
* ``STATUS`` or ``BIN`` declares the states the nodes can occupy
* ``COMPARTMENT`` or ``BLOCK`` defines a reusable behavior unit
* ``RULE`` connects a source status to a destination status through a block
* ``INITIALIZE`` sets the starting distribution or starting variables
* ``EXECUTE`` asks the runtime to run the simulation

If a script uses opinion dynamics, you will often also see:

* ``DECLARE`` for typed parameters and variables
* ``OBSERVE`` for explicit observables
* ``UPDATE`` for opinion update rules
* ``WHEN`` and ``SCHEDULE`` for conditional or time-windowed execution

Where NDQL fits in the workflow
===============================

The most common workflow is:

1. generate a graph or load an existing network
2. design the model in the visual builder or edit the NDQL text directly
3. save the model
4. generate Python and NDQL artifacts
5. execute the model and inspect plots or exported JSON

NDQL is not a replacement for the Python API. It is the textual face of the same model pipeline.
