*******************
Epidemic Blocks
*******************

The classes in this page are the Python blocks used to express epidemic custom
models. They are imported from ``ndlib.models.compartments.NDQLBlocks`` and are
typically combined inside custom transition logic or generated model code.

ExposureRate
============

Computes the exposure level induced by infected neighbors.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import ExposureRate

   exposure = ExposureRate(beta=0.1, contact_weight=1.0, mixing=1.0, infected_statuses=["Infected"])

TransmissionKernel
==================

Converts exposure into a transmission probability.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import TransmissionKernel

   kernel = TransmissionKernel(rate=1.0, saturation=1.0, source="exposure", target="transmission_probability")

DoseResponseBlock
=================

Maps dose or exposure into a response curve.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import DoseResponseBlock

   dose_response = DoseResponseBlock(shape="logistic", scale=1.5, offset=0.0)

LatencyPeriod
=============

Delays the transition from exposure to infectiousness.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import LatencyPeriod

   latency = LatencyPeriod(duration=3, distribution="fixed")

IncubationState
===============

Adds an incubation state before the infectious phase.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import IncubationState

   incubation = IncubationState(infectiousness=0.4, duration=2)

RecoveryKernel
==============

Controls how recovery hazard is computed.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import RecoveryKernel

   recovery = RecoveryKernel(gamma=0.05, source="recovery_rate")

WaningImmunity
==============

Reduces immunity over time.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import WaningImmunity

   waning = WaningImmunity(rate=0.02, delay=5)

VaccinationBlock
================

Marks vaccinated nodes or increases protection.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import VaccinationBlock

   vaccination = VaccinationBlock(coverage=0.3, efficacy=0.9)

QuarantineBlock
===============

Moves selected nodes into quarantine for a fixed duration.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import QuarantineBlock

   quarantine = QuarantineBlock(duration=7, coverage=0.8)

TestingBlock
============

Represents a testing intervention with given sensitivity and specificity.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import TestingBlock

   testing = TestingBlock(sensitivity=0.95, specificity=0.98, frequency=2)

TreatmentBlock
==============

Models treatment effects with an efficacy and a delay.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import TreatmentBlock

   treatment = TreatmentBlock(efficacy=0.7, delay=1)

HospitalizationBlock
====================

Tracks hospitalization pressure and capacity effects.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import HospitalizationBlock

   hospitalization = HospitalizationBlock(capacity=100, rate=0.2, mortality=0.05)

MortalityBlock
==============

Adds a fatality outcome to the disease progression.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import MortalityBlock

   mortality = MortalityBlock(fatality=0.02, delay=2, target_status="Removed")

ReinfectionBlock
================

Controls reinfection susceptibility after recovery.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import ReinfectionBlock

   reinfection = ReinfectionBlock(susceptibility=0.6, cooldown=3)

StrainBlock
===========

Tags or updates the active strain in a multi-strain model.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import StrainBlock

   strain = StrainBlock(strain_id=1, cross_immunity=0.3, fitness=1.1)

SuperSpreaderBlock
==================

Increases activity for superspreading nodes.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import SuperSpreaderBlock

   superspreader = SuperSpreaderBlock(activity=2.0, burst_rate=0.1)

SeasonalityBlock
================

Modulates epidemic parameters with a periodic seasonal factor.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import SeasonalityBlock

   seasonality = SeasonalityBlock(period=52, amplitude=0.3, phase=0)

ImportationBlock
================

Injects imported cases into the population.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import ImportationBlock

   importation = ImportationBlock(arrival_rate=0.01, infectious_status="Infected")

RewiringBlock
=============

Changes network edges during the simulation.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import RewiringBlock

   rewiring = RewiringBlock(rewire_rate=0.05)

CommunityMixingBlock
====================

Adjusts within-community and between-community mixing.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import CommunityMixingBlock

   mixing = CommunityMixingBlock(intra_rate=1.0, inter_rate=0.4, community_field="com")

EdgeActivationBlock
===================

Activates edges dynamically according to a threshold.

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import EdgeActivationBlock

   edge_activation = EdgeActivationBlock(threshold=0.5, duration=1)

Typical usage pattern
=====================

.. code-block:: python

   from ndlib.models.compartments.NDQLBlocks import ExposureRate, RecoveryKernel, VaccinationBlock

   exposure = ExposureRate(beta=0.1)
   recovery = RecoveryKernel(gamma=0.05)
   vaccination = VaccinationBlock(coverage=0.2, efficacy=0.9)

   # These blocks are then attached to the custom epidemic model code that
   # builds the final transition logic.
