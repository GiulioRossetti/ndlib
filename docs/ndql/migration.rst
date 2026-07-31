*******************************
Migration and Troubleshooting
*******************************

This chapter explains how to move from the older NDQL pages and how to avoid the most common mistakes.

From the old pages to the new guide
===================================

The language itself has stayed backwards compatible where possible, but the new docs are organized around the current dashboard behavior:

* explicit typed declarations
* builder-aware block families
* opinion initialization through distributions
* explicit observables and update directives

Compatibility tips
==================

* Keep classic epidemic scripts if they already work.
* Use ``TYPE CONTINUOUS_OPINION`` for continuous opinion models.
* Use ``BIN`` and ``INITIAL_OPINION_DISTRIBUTION`` for opinion initialization.
* Use ``OBSERVE`` instead of inferring plots from the model state.
* Prefer readable block aliases so the NDQL is easier to audit.

Common errors
=============

Missing state declarations
--------------------------

If a model has no statuses, the runtime cannot initialize node state correctly.

Wrong opinion distribution family
---------------------------------

Only the supported bounded families are accepted:

``uniform``, ``normal``, ``gaussian``, ``bimodal``, ``left_skewed``, ``right_skewed``, ``polarized``

Media influence count mismatch
------------------------------

``OpinionMediaInfluence`` requires one opinion value per media source.

Seed selection does not work
----------------------------

For epidemic models, the preview graph is where seed nodes are selected. If the preview is hidden by a large-network cutoff, the model uses the parameter-based infection initialization instead.

Validation habits
=================

Before saving a model:

* check the live NDQL preview
* confirm the block family matches the selected use case
* verify that initialization ratios sum to a sensible value
* make sure every block parameter is in the intended range
* regenerate the Python source once before shipping the model

Where to go next
================

If you want a practical overview, read :doc:`builder_mapping`.
If you want concrete scripts, read :doc:`examples`.
If you need the exact syntax of a directive, read :doc:`syntax`.
