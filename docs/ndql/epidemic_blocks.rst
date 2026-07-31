************************
Epidemic Blocks
************************

These blocks are used to build epidemic pipelines. In the visual builder they appear as compartments; in NDQL they behave like reusable transformation or gating units.

ExposureRate
============

Computes exposure from contacts with infectious neighbors.

Example:

.. code-block:: ndql

   COMPARTMENT exposure
   TYPE ExposureRate
   PARAM beta 0.2
   PARAM contact_weight 1.0
   PARAM mixing 1.0

TransmissionKernel
==================

Turns exposure into a transmission probability.

Example:

.. code-block:: ndql

   COMPARTMENT transmission
   TYPE TransmissionKernel
   PARAM saturation 1.0

DoseResponseBlock
=================

Maps exposure to a nonlinear infection risk.

Example:

.. code-block:: ndql

   COMPARTMENT dose_response
   TYPE DoseResponseBlock
   PARAM shape logistic
   PARAM scale 2.0
   PARAM offset 0.1

LatencyPeriod
=============

Marks a latent period before the infected state becomes active.

Example:

.. code-block:: ndql

   COMPARTMENT latency
   TYPE LatencyPeriod
   PARAM duration 2

IncubationState
===============

Represents a pre-symptomatic or incubating stage.

Example:

.. code-block:: ndql

   COMPARTMENT incubating
   TYPE IncubationState
   PARAM infectiousness 0.5
   PARAM duration 1

RecoveryKernel
==============

Encodes recovery dynamics.

Example:

.. code-block:: ndql

   COMPARTMENT recovery
   TYPE RecoveryKernel
   PARAM gamma 0.1

WaningImmunity
==============

Reduces immunity after recovery.

Example:

.. code-block:: ndql

   COMPARTMENT waning
   TYPE WaningImmunity
   PARAM rate 0.05

VaccinationBlock
================

Applies vaccination protection.

Example:

.. code-block:: ndql

   COMPARTMENT vaccination
   TYPE VaccinationBlock
   PARAM coverage 0.2
   PARAM efficacy 0.9

QuarantineBlock
===============

Isolates selected nodes and reduces their contacts.

Example:

.. code-block:: ndql

   COMPARTMENT quarantine
   TYPE QuarantineBlock
   PARAM duration 3
   PARAM coverage 0.25

TestingBlock
============

Marks tested nodes and can expose test outcomes.

Example:

.. code-block:: ndql

   COMPARTMENT testing
   TYPE TestingBlock
   PARAM sensitivity 0.95
   PARAM specificity 0.99

TreatmentBlock
==============

Models the effect of treatment on disease progression.

Example:

.. code-block:: ndql

   COMPARTMENT treatment
   TYPE TreatmentBlock
   PARAM efficacy 0.8

HospitalizationBlock
====================

Moves nodes into a managed care state.

Example:

.. code-block:: ndql

   COMPARTMENT hospital
   TYPE HospitalizationBlock
   PARAM rate 0.2
   PARAM mortality 0.05

MortalityBlock
==============

Handles death or removal from the process.

Example:

.. code-block:: ndql

   COMPARTMENT mortality
   TYPE MortalityBlock
   PARAM fatality 0.05
   PARAM target_status Removed

ReinfectionBlock
================

Reopens susceptibility after recovery.

Example:

.. code-block:: ndql

   COMPARTMENT reinfection
   TYPE ReinfectionBlock
   PARAM susceptibility 0.3

StrainBlock
===========

Tracks strain identity or strain-specific metadata.

Example:

.. code-block:: ndql

   COMPARTMENT strain
   TYPE StrainBlock
   PARAM strain_id A

SuperSpreaderBlock
==================

Models bursty transmission activity.

Example:

.. code-block:: ndql

   COMPARTMENT superspreader
   TYPE SuperSpreaderBlock
   PARAM activity 2.0
   PARAM burst_rate 0.4

SeasonalityBlock
================

Modulates transmission or activity over time.

Example:

.. code-block:: ndql

   COMPARTMENT seasonality
   TYPE SeasonalityBlock
   PARAM period 12
   PARAM amplitude 0.3

ImportationBlock
================

Injects cases from outside the network.

Example:

.. code-block:: ndql

   COMPARTMENT importation
   TYPE ImportationBlock
   PARAM arrival_rate 0.05
   PARAM infectious_status Infected

RewiringBlock
=============

Changes the contact structure while the model runs.

Example:

.. code-block:: ndql

   COMPARTMENT rewiring
   TYPE RewiringBlock
   PARAM rewire_rate 0.1

CommunityMixingBlock
====================

Adjusts transmission according to community membership.

Example:

.. code-block:: ndql

   COMPARTMENT community_mixing
   TYPE CommunityMixingBlock
   PARAM intra_rate 0.9
   PARAM inter_rate 0.1
   PARAM community_field com

EdgeActivationBlock
===================

Activates or deactivates edges according to a threshold or duration.

Example:

.. code-block:: ndql

   COMPARTMENT edge_activation
   TYPE EdgeActivationBlock
   PARAM threshold 0.5
   PARAM duration 2
