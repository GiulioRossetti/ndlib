# Network Builder and NDQL Phased Implementation Plan

This document turns [the block catalog](/Users/rossetti/PycharmProjects/ndlib/docs/network_builder_ndql_block_catalog.md) into a practical rollout plan for the remaining components.

The plan is intentionally phased so that each step produces a usable, testable increment:

- the dashboard can expose the block in the builder
- NDQL can serialize and parse the block
- generated Python can execute the model correctly
- the UI and docs stay in sync

The phases below assume the already implemented continuous-opinion core remains the baseline.

## 1. Planning Principles

The remaining blocks should be implemented in dependency order:

1. foundation blocks and shared schema changes
2. generic simulation blocks used by both epidemics and opinions
3. epidemic-specific dynamics
4. opinion-specific dynamics
5. hybrid coupling blocks
6. builder-only utilities and advanced UI polish

Each phase should end with:

- NDQL grammar support
- dashboard palette and inspector support
- Python translation support
- parser validation
- unit and smoke tests
- documentation updates

## 2. Phase 0 - Foundation and Schema

Goal: make the builder and NDQL capable of expressing typed model components cleanly before adding more behavior.

### Scope

- `Parameter`
- `Constant`
- `Variable`
- `Distribution`
- `Selector`
- `Filter`
- `Aggregator`
- `Kernel`
- `Transform`
- `Compose`
- `Schedule`
- `Observe`
- `ClampNormalize`

### Why first

These blocks define the common language used by all future blocks. Without them, later epidemic and opinion blocks will keep requiring special-case handling.

### Deliverables

- typed block metadata in the dashboard
- a shared parameter schema and validation layer
- NDQL declarations for typed values and typed initializers
- parser support for typed model sections
- code generation helpers that reduce duplication across block families

### Exit criteria

- one shared block schema can describe both epidemic and opinion blocks
- generated NDQL is still backward compatible with current scripts
- the parser accepts the new declarations without breaking old ones

## 3. Phase 1 - Shared Execution Primitives

Goal: implement the generic control-flow and value-transformation blocks that most model families will reuse.

### Scope

- `Compose`
- `Schedule`
- `Observe`
- `ClampNormalize`
- `Filter`
- `Aggregator`
- `Transform`
- `Kernel`
- `Selector`

### Intended use

These blocks are the building blocks for:

- bounded-confidence filters
- partner selection bias
- time-gated interventions
- summaries and observables
- deterministic and stochastic update rules

### Suggested implementation order

1. `Compose`
2. `Transform`
3. `ClampNormalize`
4. `Filter`
5. `Selector`
6. `Aggregator`
7. `Kernel`
8. `Schedule`
9. `Observe`

### Exit criteria

- the builder can express nested rule logic without custom hard-coded branches
- observables can be serialized in NDQL rather than inferred indirectly
- at least one shared block can be reused by both epidemic and opinion examples

## 4. Phase 2 - Epidemic-Specific Blocks

Goal: extend the epidemic side with explicit model components instead of relying only on transition shortcuts.

### Scope

- `ExposureRate`
- `TransmissionKernel`
- `DoseResponseBlock`
- `LatencyPeriod`
- `IncubationState`
- `RecoveryKernel`
- `WaningImmunity`
- `VaccinationBlock`
- `QuarantineBlock`
- `TestingBlock`
- `TreatmentBlock`
- `HospitalizationBlock`
- `MortalityBlock`
- `ReinfectionBlock`
- `StrainBlock`
- `SuperSpreaderBlock`
- `SeasonalityBlock`
- `ImportationBlock`
- `RewiringBlock`
- `CommunityMixingBlock`
- `EdgeActivationBlock`

### Suggested implementation order

1. `ExposureRate`, `TransmissionKernel`, `DoseResponseBlock`
2. `LatencyPeriod`, `IncubationState`, `RecoveryKernel`, `WaningImmunity`
3. `VaccinationBlock`, `QuarantineBlock`, `TestingBlock`, `TreatmentBlock`
4. `HospitalizationBlock`, `MortalityBlock`, `ReinfectionBlock`
5. `SeasonalityBlock`, `ImportationBlock`, `SuperSpreaderBlock`
6. `RewiringBlock`, `CommunityMixingBlock`, `EdgeActivationBlock`
7. `StrainBlock`

### Why this order

The first group covers core epidemiological mechanics. The later groups add structural complexity, interventions, and time-varying behavior.

### Exit criteria

- one SEIR-like model can be described entirely through blocks
- intervention blocks can be scheduled and combined
- graph-level dynamics can be expressed without custom code

## 5. Phase 3 - Opinion-Specific Blocks

Goal: make continuous and discrete opinion dynamics first-class citizens in the builder and NDQL.

### Scope

- `OpinionDistribution`
- `OpinionStubbornness`
- `OpinionNoise`
- `OpinionPolarization`
- `OpinionMediaInfluence`
- `OpinionTrustFilter`
- `OpinionConsensusBlock`
- `OpinionRepulsion`
- `OpinionAssimilation`
- `OpinionExternalField`
- `OpinionMultiTopic`
- `OpinionLabelSwitch`
- `OpinionBoundedDrift`

### Suggested implementation order

1. `OpinionDistribution`
2. `OpinionStubbornness`, `OpinionNoise`
3. `OpinionTrustFilter`, `OpinionConsensusBlock`
4. `OpinionAssimilation`, `OpinionRepulsion`, `OpinionBoundedDrift`
5. `OpinionPolarization`, `OpinionExternalField`
6. `OpinionMultiTopic`
7. `OpinionLabelSwitch`
8. `OpinionMediaInfluence` enhancements if the model needs more than simple media mixing

### Notes

- `OpinionDistribution` should become the canonical schema for initialization, even where current opinion starters already support distributions.
- `OpinionLabelSwitch` is the main bridge for discrete opinion dynamics.
- `OpinionBoundedDrift` is useful as a low-level update primitive for several continuous models.

### Exit criteria

- the builder can express both continuous and discrete opinion models without custom templates
- opinion initialization, update, and observability are all explicit in NDQL
- opinion models can round-trip through save, parse, and execution

## 6. Phase 4 - Hybrid Coupling Blocks

Goal: express models where opinions and epidemics influence one another.

### Scope

- `OpinionAffectsInfection`
- `OpinionAffectsRecovery`
- `OpinionAffectsContactRate`
- `InfectionAffectsOpinion`
- `StatusDependentOpinionUpdate`
- `EpidemicDependentBias`
- `AttributeCoupling`
- `PolicyIntervention`
- `CommunityCoupling`

### Suggested implementation order

1. `AttributeCoupling`
2. `OpinionAffectsContactRate`
3. `OpinionAffectsInfection`
4. `OpinionAffectsRecovery`
5. `StatusDependentOpinionUpdate`
6. `EpidemicDependentBias`
7. `PolicyIntervention`
8. `InfectionAffectsOpinion`
9. `CommunityCoupling`

### Exit criteria

- one model can combine epidemiological status and opinion state in the same pipeline
- the builder can express coupled rules without hard-coded model templates
- coupled models can be validated with both NDQL and generated Python

## 7. Phase 5 - Builder-Only Utility Blocks

Goal: improve usability for complex models without changing the runtime semantics directly.

Status: implemented in the current branch for the utility runtime blocks, parser whitelist, dashboard palette exposure, and NDQL/Python round-trip support.

### Scope

- `SeedSelection`
- `NodeRoleAssignment`
- `AttributeInitializer`
- `GraphImport`
- `CommunityAssignment`
- `RuleAlias`
- `PreviewObservable`
- `ValidationHint`

### Suggested implementation order

1. `SeedSelection`
2. `NodeRoleAssignment`
3. `AttributeInitializer`
4. `CommunityAssignment`
5. `PreviewObservable`
6. `ValidationHint`
7. `RuleAlias`
8. `GraphImport`

### Exit criteria

- the builder can express seed placement and roles without manual JSON editing
- previews explain what the model will visualize before execution
- validation errors are shown before the model is saved

Phase 5 is complete in the current branch.

## 8. Phase 6 - NDQL Language Expansion

Goal: make NDQL expressive enough to support all the blocks above without special-case syntax.

Status: implemented in the current branch for typed declarations, observables, update directives, and parser-supported schedule/condition annotations.

### Required language features

- typed declarations
- typed initializers
- expression-based updates
- explicit observables
- richer conditional composition
- time/schedule annotations
- reusable aliases for nested block trees

### Recommended syntax areas to add next

- `DECLARE VARIABLE`
- `DECLARE PARAM`
- `DECLARE GLOBAL`
- `INITIALIZE ... DISTRIBUTION ...`
- `UPDATE ... = ...`
- `OBSERVE ... AS ...`
- `WHEN ...`
- `SCHEDULE ...`

### Exit criteria

- old NDQL remains valid
- new NDQL can describe both epidemic and opinion dynamics with fewer hard-coded shortcuts
- the parser can translate the richer scripts into executable Python without losing meaning

Phase 6 is complete in the current branch.

## 9. Phase 7 - Builder Dashboard Integration

Goal: integrate the remaining block families into the visual builder so the dashboard, NDQL preview, and generated Python all stay synchronized.

Status: implemented in the current branch for the model directives panel, live NDQL preview, and custom model save/load path.

### Scope

- expose the remaining blocks in the correct builder palettes
- add or refine inspector controls for every block parameter
- keep default values aligned between the builder, NDQL, and Python generator
- make the live NDQL preview reflect all supported block types
- ensure the graph visualization and opinion distribution panels behave correctly for each model family
- preserve use-case filtering so small model builders stay simple

### Key integration tasks

1. wire each new block type into the block catalog UI
2. add default node templates or starter examples when a family benefits from them
3. update the inspector to support typed inputs, ranges, choices, and nested references
4. enforce validation before save and before simulation
5. verify that generated NDQL round-trips through reload and parser execution
6. keep the builder usable on smaller screens and for large models

### Exit criteria

- the builder can construct the implemented block families without manual JSON edits
- the NDQL preview matches the saved JSON and the generated Python code
- each use case shows only the blocks that make sense, unless advanced mode is enabled
- dashboard visualization remains consistent for both network graphs and opinion distributions

## 10. Phase 8 - Complete NDQL User Manual

Goal: write a complete user-facing NDQL manual that explains both the language and the builder output in practical terms.

Status: implemented in the current branch as a dedicated NDQL manual with syntax reference, block family coverage, worked examples, builder guidance, and troubleshooting notes.

### Scope

- rationale for NDQL and how it maps to the builder
- syntax reference for all top-level directives
- detailed block descriptions grouped by family
- use-case guidance for epidemics, opinions, and coupled models
- examples for every major component
- migration notes from legacy scripts to typed NDQL
- troubleshooting and validation guidance

### Recommended structure

1. introduction and design goals
2. core NDQL grammar and syntax rules
3. declaration sections
4. initialization patterns
5. block reference by category
6. examples for epidemic models
7. examples for opinion models
8. examples for coupled models
9. builder round-trip examples
10. parser and Python translation notes
11. validation and debugging advice

### Example coverage expectations

The manual should include plenty of worked examples for each component family:

- one minimal example
- one realistic builder-generated example
- one advanced example with multiple blocks composed together
- one example showing invalid or ambiguous usage and the expected error

### Exit criteria

- a user can understand NDQL without opening the builder source code
- the manual explains why each block exists, not only what it does
- every implemented block family has a documented use case and example
- the manual matches the dashboard and parser behavior at the time of release

## 11. Validation Strategy Per Phase

Every phase should ship with the same verification pattern.

### Tests

- parser round-trip tests for the new NDQL syntax
- dashboard generation tests for the new block payloads
- Python code generation tests for the compiled custom model
- runtime smoke tests on small graphs
- regression tests for backwards compatibility

### Documentation

- update the block catalog implementation status
- add one short usage example per implemented block family
- update the builder guide when the visible UI changes

### Manual checks

- builder palette contains the block in the correct use case
- inspector fields render with the expected default values
- live NDQL preview reflects the block exactly
- generated Python remains readable and deterministic

## 12. Recommended Delivery Order

If the remaining work must be broken into smaller releases, the safest order is:

1. phase 0 foundation
2. phase 1 shared execution primitives
3. phase 3 opinion blocks
4. phase 2 epidemic blocks
5. phase 4 hybrid coupling
6. phase 5 builder-only utilities
7. phase 6 NDQL expansion and cleanup

That order front-loads the abstractions that all later blocks depend on, while allowing opinion and epidemic feature work to proceed as separate streams once the shared primitives are stable.

## 13. Practical Cut Lines

If implementation has to stop between phases, prefer stopping at these points:

- after a shared schema or parser change
- after a complete family of blocks is round-trippable
- after tests and docs are updated together

Avoid stopping mid-family, because partially exposed blocks tend to leave the builder, the NDQL preview, and the parser out of sync.
