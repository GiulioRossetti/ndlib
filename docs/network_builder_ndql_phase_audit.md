# Network Builder and NDQL Phase Audit

Audit date: 2026-07-29

This document checks the implementation described in
[network_builder_ndql_phased_implementation.md](/Users/rossetti/PycharmProjects/ndlib/docs/network_builder_ndql_phased_implementation.md)
against the current code, parser, tests, and dashboard UI.

Status key:

- `done`: implemented and verified at the code/test/UI level
- `partial`: present, but not yet fully closed or exhaustively verified
- `missing`: not found in the current tree

## Overall Read

- Phase 1: `done`
- Phase 2: `done`
- Phase 3: `done`
- Phase 4: `done`
- Phase 5: `done`
- Phase 6: `done`
- Phase 7: `partial`
- Phase 8: `done`

The main remaining gaps are completeness gaps, not missing subsystems:

- phase 0 still lacks a clearly centralized shared schema/validation abstraction
- phase 2 now has a canonical end-to-end builder starter for the full late-stage epidemic block set
- phase 7 still has some generic inspector controls and some verification paths that are not yet exhaustive across all families
- validation coverage is representative rather than complete across every block combination

## Phase 0 - Foundation and Schema

Scope items:

- `Parameter` - `done`
- `Constant` - `done`
- `Variable` - `done`
- `Distribution` - `done`
- `Selector` - `done`
- `Filter` - `done`
- `Aggregator` - `done`
- `Kernel` - `done`
- `Transform` - `done`
- `Compose` - `done`
- `Schedule` - `done`
- `Observe` - `done`
- `ClampNormalize` - `done`

Deliverables:

- typed block metadata in the dashboard - `done`
- a shared parameter schema and validation layer - `partial`
- NDQL declarations for typed values and typed initializers - `done`
- parser support for typed model sections - `done`
- code generation helpers that reduce duplication across block families - `done`

Exit criteria:

- one shared block schema can describe both epidemic and opinion blocks - `partial`
- generated NDQL is still backward compatible with current scripts - `done`
- the parser accepts the new declarations without breaking old ones - `done`

Notes:

- The code has strong shared helpers and coercion logic, but the schema/validation layer is still mostly implicit in dashboard/server helpers and block constructors rather than a single explicit registry.

## Phase 1 - Shared Execution Primitives

Scope items:

- `Compose` - `done`
- `Schedule` - `done`
- `Observe` - `done`
- `ClampNormalize` - `done`
- `Filter` - `done`
- `Aggregator` - `done`
- `Transform` - `done`
- `Kernel` - `done`
- `Selector` - `done`

Intended use:

- bounded-confidence filters - `done`
- partner selection bias - `done`
- time-gated interventions - `done`
- summaries and observables - `done`
- deterministic and stochastic update rules - `done`

Suggested implementation order:

- `Compose` - `done`
- `Transform` - `done`
- `ClampNormalize` - `done`
- `Filter` - `done`
- `Selector` - `done`
- `Aggregator` - `done`
- `Kernel` - `done`
- `Schedule` - `done`
- `Observe` - `done`

Exit criteria:

- the builder can express nested rule logic without custom hard-coded branches - `done`
- observables can be serialized in NDQL rather than inferred indirectly - `done`
- at least one shared block can be reused by both epidemic and opinion examples - `done`

## Phase 2 - Epidemic-Specific Blocks

Scope items:

- `ExposureRate` - `done`
- `TransmissionKernel` - `done`
- `DoseResponseBlock` - `done`
- `LatencyPeriod` - `done`
- `IncubationState` - `done`
- `RecoveryKernel` - `done`
- `WaningImmunity` - `done`
- `VaccinationBlock` - `done`
- `QuarantineBlock` - `done`
- `TestingBlock` - `done`
- `TreatmentBlock` - `done`
- `HospitalizationBlock` - `done`
- `MortalityBlock` - `done`
- `ReinfectionBlock` - `done`
- `StrainBlock` - `done`
- `SuperSpreaderBlock` - `done`
- `SeasonalityBlock` - `done`
- `ImportationBlock` - `done`
- `RewiringBlock` - `done`
- `CommunityMixingBlock` - `done`
- `EdgeActivationBlock` - `done`

Suggested implementation order:

- `ExposureRate`, `TransmissionKernel`, `DoseResponseBlock` - `done`
- `LatencyPeriod`, `IncubationState`, `RecoveryKernel`, `WaningImmunity` - `done`
- `VaccinationBlock`, `QuarantineBlock`, `TestingBlock`, `TreatmentBlock` - `done`
- `HospitalizationBlock`, `MortalityBlock`, `ReinfectionBlock` - `done`
- `SeasonalityBlock`, `ImportationBlock`, `SuperSpreaderBlock` - `done`
- `RewiringBlock`, `CommunityMixingBlock`, `EdgeActivationBlock` - `done`
- `StrainBlock` - `done`

Why this order:

- the first group covers core epidemiological mechanics - `done`
- the later groups add structural complexity, interventions, and time-varying behavior - `done`

Exit criteria:

- one SEIR-like model can be described entirely through blocks - `done`
- intervention blocks can be scheduled and combined - `done`
- graph-level dynamics can be expressed without custom code - `done`

Notes:

- The runtime, parser, and tests now cover the named epidemic blocks, and the builder includes a canonical late-stage epidemic starter that exercises the full stack end to end.

## Phase 3 - Opinion-Specific Blocks

Scope items:

- `OpinionDistribution` - `done`
- `OpinionStubbornness` - `done`
- `OpinionNoise` - `done`
- `OpinionPolarization` - `done`
- `OpinionMediaInfluence` - `done`
- `OpinionTrustFilter` - `done`
- `OpinionConsensusBlock` - `done`
- `OpinionRepulsion` - `done`
- `OpinionAssimilation` - `done`
- `OpinionExternalField` - `done`
- `OpinionMultiTopic` - `done`
- `OpinionLabelSwitch` - `done`
- `OpinionBoundedDrift` - `done`

Suggested implementation order:

- `OpinionDistribution` - `done`
- `OpinionStubbornness`, `OpinionNoise` - `done`
- `OpinionTrustFilter`, `OpinionConsensusBlock` - `done`
- `OpinionAssimilation`, `OpinionRepulsion`, `OpinionBoundedDrift` - `done`
- `OpinionPolarization`, `OpinionExternalField` - `done`
- `OpinionMultiTopic` - `done`
- `OpinionLabelSwitch` - `done`
- `OpinionMediaInfluence` enhancements - `done`

Notes:

- `OpinionDistribution` is the canonical initialization schema in the builder - `done`
- `OpinionLabelSwitch` bridges discrete opinion dynamics - `done`
- `OpinionBoundedDrift` is available as a low-level primitive - `done`

Exit criteria:

- the builder can express both continuous and discrete opinion models without custom templates - `done`
- opinion initialization, update, and observability are all explicit in NDQL - `done`
- opinion models can round-trip through save, parse, and execution - `done`

## Phase 4 - Hybrid Coupling Blocks

Scope items:

- `OpinionAffectsInfection` - `done`
- `OpinionAffectsRecovery` - `done`
- `OpinionAffectsContactRate` - `done`
- `InfectionAffectsOpinion` - `done`
- `StatusDependentOpinionUpdate` - `done`
- `EpidemicDependentBias` - `done`
- `AttributeCoupling` - `done`
- `PolicyIntervention` - `done`
- `CommunityCoupling` - `done`

Suggested implementation order:

- `AttributeCoupling` - `done`
- `OpinionAffectsContactRate` - `done`
- `OpinionAffectsInfection` - `done`
- `OpinionAffectsRecovery` - `done`
- `StatusDependentOpinionUpdate` - `done`
- `EpidemicDependentBias` - `done`
- `PolicyIntervention` - `done`
- `InfectionAffectsOpinion` - `done`
- `CommunityCoupling` - `done`

Exit criteria:

- one model can combine epidemiological status and opinion state in the same pipeline - `done`
- the builder can express coupled rules without hard-coded model templates - `done`
- coupled models can be validated with both NDQL and generated Python - `done`

## Phase 5 - Builder-Only Utility Blocks

Scope items:

- `SeedSelection` - `done`
- `NodeRoleAssignment` - `done`
- `AttributeInitializer` - `done`
- `GraphImport` - `done`
- `CommunityAssignment` - `done`
- `RuleAlias` - `done`
- `PreviewObservable` - `done`
- `ValidationHint` - `done`

Exit criteria:

- the builder can express seed placement and roles without manual JSON editing - `done`
- previews explain what the model will visualize before execution - `done`
- validation errors are shown before the model is saved - `done`

## Phase 6 - NDQL Language Expansion

Required language features:

- typed declarations - `done`
- typed initializers - `done`
- expression-based updates - `done`
- explicit observables - `done`
- richer conditional composition - `done`
- time/schedule annotations - `done`
- reusable aliases for nested block trees - `done`

Recommended syntax areas to add next:

- `DECLARE VARIABLE` - `done`
- `DECLARE PARAM` - `done`
- `DECLARE GLOBAL` - `done`
- `INITIALIZE ... DISTRIBUTION ...` - `done`
- `UPDATE ... = ...` - `done`
- `OBSERVE ... AS ...` - `done`
- `WHEN ...` - `done`
- `SCHEDULE ...` - `done`

Exit criteria:

- old NDQL remains valid - `done`
- new NDQL can describe both epidemic and opinion dynamics with fewer hard-coded shortcuts - `done`
- the parser can translate the richer scripts into executable Python without losing meaning - `done`

## Phase 7 - Builder Dashboard Integration

Scope items:

- expose the remaining blocks in the correct builder palettes - `done`
- add or refine inspector controls for every block parameter - `partial`
- keep default values aligned between the builder, NDQL, and Python generator - `partial`
- make the live NDQL preview reflect all supported block types - `done`
- ensure the graph visualization and opinion distribution panels behave correctly for each model family - `partial`
- preserve use-case filtering so small model builders stay simple - `done`

Key integration tasks:

- wire each new block type into the block catalog UI - `done`
- add default node templates or starter examples when a family benefits from them - `partial`
- update the inspector to support typed inputs, ranges, choices, and nested references - `partial`
- enforce validation before save and before simulation - `partial`
- verify that generated NDQL round-trips through reload and parser execution - `partial`
- keep the builder usable on smaller screens and for large models - `partial`

Exit criteria:

- the builder can construct the implemented block families without manual JSON edits - `done`
- the NDQL preview matches the saved JSON and the generated Python code - `partial`
- each use case shows only the blocks that make sense, unless advanced mode is enabled - `done`
- dashboard visualization remains consistent for both network graphs and opinion distributions - `partial`

Notes:

- The browser flows now work for the key continuous-opinion path and the network graph no longer crashes on Cytoscape `fit()`, but the UI still needs broader end-to-end coverage across all families and screen sizes.

## Phase 8 - Complete NDQL User Manual

Scope items:

- rationale for NDQL and how it maps to the builder - `done`
- syntax reference for all top-level directives - `done`
- detailed block descriptions grouped by family - `done`
- use-case guidance for epidemics, opinions, and coupled models - `done`
- examples for every major component - `done`
- migration notes from legacy scripts to typed NDQL - `done`
- troubleshooting and validation guidance - `done`

Recommended structure:

- introduction and design goals - `done`
- core NDQL grammar and syntax rules - `done`
- declaration sections - `done`
- initialization patterns - `done`
- block reference by category - `done`
- examples for epidemic models - `done`
- examples for opinion models - `done`
- examples for coupled models - `done`
- builder round-trip examples - `done`
- parser and Python translation notes - `done`
- validation and debugging advice - `done`

Example coverage expectations:

- one minimal example - `done`
- one realistic builder-generated example - `done`
- one advanced example with multiple blocks composed together - `done`
- one example showing invalid or ambiguous usage and the expected error - `done`

Exit criteria:

- a user can understand NDQL without opening the builder source code - `done`
- the manual explains why each block exists, not only what it does - `done`
- every implemented block family has a documented use case and example - `done`
- the manual matches the dashboard and parser behavior at the time of release - `done`

## Validation Strategy

Tests:

- parser round-trip tests for the new NDQL syntax - `done`
- dashboard generation tests for the new block payloads - `done`
- Python code generation tests for the compiled custom model - `done`
- runtime smoke tests on small graphs - `done`
- regression tests for backwards compatibility - `done`

Documentation:

- update the block catalog implementation status - `done`
- add one short usage example per implemented block family - `done`
- update the builder guide when the visible UI changes - `done`

Manual checks:

- builder palette contains the block in the correct use case - `done`
- inspector fields render with the expected default values - `partial`
- live NDQL preview reflects the block exactly - `done`
- generated Python remains readable and deterministic - `done`

## Gap Closure Plan

The remaining work is to turn the partials into explicit, repeatable coverage.

1. Introduce a shared schema/validation registry for phase 0.
   - Make the block metadata a first-class source of truth instead of deriving it indirectly from dashboard payloads and per-block helpers.
   - Use the registry to drive inspector widgets, default coercion, and validation messages.

2. Add canonical end-to-end epidemic examples for phase 2.
   - Provide a builder starter that composes the late-stage epidemic blocks into a readable SEIR-like pipeline.
   - Add parser and runtime smoke tests for the late-stage blocks together, not only individually.

3. Finish the remaining phase-7 inspector work.
   - Replace generic JSON-ish fields with purpose-built controls where the parameter shape is known.
   - Add explicit validation before save and before simulation for invalid ranges, missing nested references, and incompatible combinations.

4. Expand round-trip verification.
   - Add one representative model per block family and one coupled model that exercises the mixed families end to end.
   - Verify save -> reload -> parse -> Python generation in a single test path for each representative model.

5. Tighten dashboard QA for large and small layouts.
   - Validate the network graph and opinion distribution panels on small graphs, large graphs, and continuous-opinion models with multiple starter distributions.
   - Check that the UI remains usable on narrower screens and that the visualization switches remain deterministic.

6. Extend the manual only where the runtime still has ambiguity.
   - Add one worked example for the remaining edge cases once the phase-0 schema and phase-7 inspector work are stabilized.
   - Keep the manual in lockstep with any new validation or UI behavior.
