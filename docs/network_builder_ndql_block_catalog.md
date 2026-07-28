# Network Builder and NDQL Block Catalog

This document describes additional blocks that would make the visual network builder and NDQL substantially more expressive for both epidemic and opinion dynamics.

The goal is not to implement everything at once. This is a complete design catalog for future work.

## 1. Design Goals

The builder and NDQL should support:

- typed node variables, edge variables, and global parameters
- continuous and discrete state spaces
- stochastic, deterministic, and hybrid update rules
- conditional compositions and nested rule trees
- coupling between epidemic and opinion dynamics
- reusable blocks that can be combined into more complex models
- backward compatibility with the current `STATUS / COMPARTMENT / RULE / INITIALIZE` syntax

The most important architectural change is to move from a small set of hard-coded compartment types to a typed block system where every block has:

- a scope
- a type
- a parameter schema
- an execution semantics
- an NDQL serialization

## 1.1 Implementation Status

The following items from this catalog are implemented in the current dashboard and parser branch:

- continuous-opinion initial opinion distributions
- `OpinionDistanceThreshold`
- `OpinionSelectionBias`
- `OpinionCompromise`
- `OpinionNormalization`
- `OpinionZealot`
- continuous-opinion builder palette support
- continuous-opinion NDQL serialization in the dashboard
- continuous-opinion custom Python model generation
- parser execution for the builder-emitted continuous-opinion NDQL subset
- typed NDQL declarations and observables in the builder payload and parser
- discrete-opinion initial class percentages
- zealot selection in the dashboard for `VoterZealotModel`
- media opinion count and per-media opinion values for `AlgorithmicBiasMediaModel`
- zealot block round-trip and runtime validation for continuous-opinion custom models

The remaining blocks below stay in the catalog as future implementation targets.

## 2. Current Gaps

The current builder is strong for simple epidemic flows and generic conditional rules, but it is weak for:

- opinion-specific initialization
- biased partner selection
- bounded-confidence thresholds
- compromise/averaging rules
- multi-stage opinion update kernels
- opinion-media coupling
- epidemic-opinion feedback loops
- heterogeneous node or edge attributes that affect update dynamics

These are the main reasons why a generic `NodeNumericalVariable` block is not enough for continuous opinion models.

## 3. Recommended NDQL Shape

The NDQL grammar should stay line-oriented and human readable, but it should become typed and compositional.

Recommended top-level sections:

```ndql
MODEL MyModel
TYPE EPIDEMIC | OPINION | COUPLED

DECLARE STATUS Susceptible
DECLARE VARIABLE opinion TYPE continuous RANGE [0,1]
DECLARE VARIABLE label TYPE discrete VALUES [A,B,C]
DECLARE PARAM epsilon TYPE float DEFAULT 0.1
DECLARE PARAM k TYPE int DEFAULT 3

INITIALIZE
SET STATUS Susceptible 0.95
SET VARIABLE opinion DISTRIBUTION bimodal
SET VARIABLE label SAMPLE [A,B,C] WEIGHTS [0.5,0.3,0.2]

BLOCK bounded_confidence TYPE OpinionDistanceThreshold
PARAM epsilon 0.1

RULE FROM Susceptible TO Infected USING infection_kernel
WHEN opinion > 0.5
UPDATE opinion = clamp(opinion + mu * (neighbor_opinion - opinion), 0, 1)

OBSERVE opinion AS bins 20
```

### 3.1 Compatibility Rules

The new NDQL should accept the current syntax as sugar for the richer grammar.

Examples:

- `STATUS` can map to `DECLARE STATUS`
- `COMPARTMENT` can map to `BLOCK`
- `PARAM` remains valid
- `IF ... THEN ... ELSE ... AS ...` remains valid as a composition shorthand
- old epidemic-only scripts should still parse unchanged

## 4. Core Blocks

These blocks are useful for both epidemics and opinions.

| Block | Purpose | Key Parameters | Notes |
| --- | --- | --- | --- |
| `Parameter` | Declares a typed model parameter | `name`, `type`, `default`, `range`, `choices` | Needed for validation and UI generation |
| `Constant` | Declares an immutable scalar or vector | `value`, `type` | Useful for fixed coefficients |
| `Variable` | Declares node, edge, or global variables | `scope`, `type`, `range` | The main abstraction for opinion values and node attributes |
| `Distribution` | Samples initial values | `name`, `family`, `params`, `bounds` | Covers uniform, normal, bimodal, beta, truncated, etc. |
| `Selector` | Picks nodes, neighbors, edges, or media | `scope`, `bias`, `policy` | Required for stochastic partner choice and targeted interventions |
| `Filter` | Restricts the active neighborhood or event set | `predicate`, `window`, `threshold` | Used for confidence bounds, age filters, community filters |
| `Aggregator` | Computes summary statistics | `mode`, `weights`, `window` | Mean, median, majority, quantile, min, max |
| `Kernel` | Defines the update law | `formula`, `rate`, `step`, `clamp` | Compromise, infection hazard, decay, reinforcement |
| `Transform` | Applies deterministic state transformation | `expression`, `target`, `clamp` | Useful for opinion normalization and status mutation |
| `Compose` | Combines blocks conditionally | `condition`, `if_true`, `if_false` | Generalizes `ConditionalComposition` |
| `Schedule` | Activates blocks over time | `start`, `end`, `period`, `phase` | Enables phased interventions and seasonal effects |
| `Observe` | Requests a plot/exportable observable | `variable`, `bins`, `range`, `mode` | Needed for opinion distributions and epidemic prevalence |
| `ClampNormalize` | Enforces value bounds | `min`, `max`, `renormalize` | Essential for bounded continuous opinions |

## 5. Epidemic-Specific Blocks

These blocks make epidemic models more expressive than the current status-transition palette.

| Block | Purpose | Key Parameters | Example Uses |
| --- | --- | --- | --- |
| `ExposureRate` | Computes contact-driven exposure intensity | `beta`, `contact_weight`, `mixing` | Infection hazards, partial immunity, contact heterogeneity |
| `TransmissionKernel` | Converts exposure into infection probability | `function`, `saturation`, `dose_response` | Stochastic infection, edge-weighted transmission |
| `LatencyPeriod` | Models a latent/exposed period | `duration`, `distribution` | SEIR-like dynamics |
| `IncubationState` | Represents pre-symptomatic infectiousness | `infectiousness`, `duration` | Multi-stage infection dynamics |
| `RecoveryKernel` | Defines recovery probability or rate | `gamma`, `hazard`, `distribution` | SIS, SIR, SEIR variants |
| `WaningImmunity` | Loss of immunity and return to susceptible | `rate`, `delay` | SIRS and recurrent outbreaks |
| `VaccinationBlock` | Preventive immunization or protection | `coverage`, `efficacy`, `priority` | Campaigns and interventions |
| `QuarantineBlock` | Removes or isolates nodes from contacts | `duration`, `trigger`, `coverage` | Isolation, lockdown, contact tracing |
| `TestingBlock` | Detects infection or risk state | `sensitivity`, `specificity`, `frequency` | Surveillance and diagnosis |
| `TreatmentBlock` | Applies recovery acceleration | `efficacy`, `delay`, `capacity` | Therapy, care saturation, triage |
| `HospitalizationBlock` | Moves nodes to a managed state | `capacity`, `rate`, `mortality` | Severe disease models |
| `MortalityBlock` | Absorbing death/removal dynamics | `fatality`, `delay`, `cause` | Mortality-aware epidemics |
| `ReinfectionBlock` | Enables repeated infection | `susceptibility`, `cooldown` | Endemic models |
| `StrainBlock` | Supports multiple pathogen strains | `strain_id`, `cross_immunity`, `fitness` | Variant and mutation models |
| `SuperSpreaderBlock` | Adds heavy-tail transmission behavior | `activity`, `burst_rate` | Superspreading events |
| `SeasonalityBlock` | Modulates transmission over time | `period`, `amplitude`, `phase` | Seasonal waves |
| `ImportationBlock` | Adds external infection events | `arrival_rate`, `source` | Imported cases and spillover |
| `RewiringBlock` | Alters contact graph dynamically | `rewire_rate`, `preference` | Adaptive behavior, distancing |
| `CommunityMixingBlock` | Controls between-community contact | `intra_rate`, `inter_rate` | Structured mixing, SBM-like dynamics |
| `EdgeActivationBlock` | Activates or deactivates contacts | `threshold`, `duration` | Temporal network effects |
| `DoseResponseBlock` | Maps exposure to infection probability | `shape`, `scale`, `offset` | Nonlinear hazard functions |

## 6. Opinion-Specific Blocks

These are the blocks needed for continuous and discrete opinion models.

| Block | Purpose | Key Parameters | Example Uses |
| --- | --- | --- | --- |
| `OpinionDistribution` | Seeds initial opinions | `family`, `params`, `bounds` | Uniform, normal, bimodal, polarized |
| `OpinionDistanceThreshold` | Bounded confidence gate | `epsilon`, `metric`, `strict` | Deffuant, HK-like filtering |
| `OpinionSelectionBias` | Biases who interacts with whom | `gamma`, `bias_mode`, `fallback` | Algorithmic bias partner selection |
| `OpinionCompromise` | Performs averaging or convergence | `mu`, `asymmetry`, `clamp` | Deffuant-style update rules |
| `OpinionStubbornness` | Reduces responsiveness to neighbors | `theta`, `memory`, `floor` | Friedkin-Johnsen-like behavior |
| `OpinionZealot` | Immutable or nearly immutable opinion holder | `fixed_value`, `mask`, `share` | Zealots and committed agents |
| `OpinionNoise` | Adds random perturbation to opinions | `sigma`, `distribution` | Social noise and exploration |
| `OpinionQuantization` | Converts continuous opinions into bins | `bins`, `rounding`, `labels` | Discrete opinion outputs |
| `OpinionNormalization` | Enforces bounded range | `min`, `max`, `renormalize` | Keeps values in `[0,1]` |
| `OpinionMemory` | Retains past opinion values | `alpha`, `window`, `decay` | Anchoring and inertia |
| `OpinionPolarization` | Pushes opinions toward extremes | `strength`, `attractor_points` | Polarization and echo chambers |
| `OpinionMediaInfluence` | Mixes nodes with one or more media sources | `k`, `media_opinions`, `weights` | Algorithmic bias and media models |
| `OpinionTrustFilter` | Trust/distrust-based influence gating | `trust_threshold`, `signed`, `asymmetry` | Homophily, selective exposure |
| `OpinionConsensusBlock` | Aggregates neighborhood opinion | `mode`, `weights`, `confidence` | Mean, median, majority, weighted consensus |
| `OpinionRepulsion` | Moves agents away from dissimilar neighbors | `epsilon`, `strength` | Antagonistic or anti-consensus dynamics |
| `OpinionAssimilation` | Positive influence toward neighbors | `rate`, `window` | Classic alignment models |
| `OpinionExternalField` | Pushes opinions toward a target value | `target`, `strength`, `schedule` | Propaganda, policy pressure, institutions |
| `OpinionMultiTopic` | Supports multiple opinion dimensions | `topics`, `coupling`, `correlation` | Multi-issue political dynamics |
| `OpinionLabelSwitch` | Discrete opinion reassignment | `from`, `to`, `probability` | Voter-like and categorical models |
| `OpinionBoundedDrift` | Repeated drift under a bounded constraint | `step`, `bounds`, `noise` | Low-level continuous update kernel |

## 7. Hybrid Coupling Blocks

These blocks are needed when epidemic and opinion dynamics interact.

| Block | Purpose | Key Parameters | Example Uses |
| --- | --- | --- | --- |
| `OpinionAffectsInfection` | Opinion changes infection risk | `mapping`, `strength`, `threshold` | Risk perception, vaccine hesitancy |
| `OpinionAffectsRecovery` | Opinion changes recovery or treatment seeking | `mapping`, `strength` | Care-seeking behavior |
| `OpinionAffectsContactRate` | Opinion changes contact frequency | `mapping`, `social_distance` | Distancing behavior |
| `InfectionAffectsOpinion` | Infection changes beliefs or sentiment | `direction`, `lag`, `strength` | Trauma, stigma, misinformation |
| `StatusDependentOpinionUpdate` | Opinion update depends on epidemic status | `status_filter`, `kernel` | Different behaviors for S/I/R nodes |
| `EpidemicDependentBias` | Biases selection or compromise based on status | `status_weight`, `cross_status_factor` | Separate dynamics for infected and non-infected nodes |
| `AttributeCoupling` | Couples any graph attribute into either model family | `attribute`, `source`, `target` | Age, community, activity, ideology |
| `PolicyIntervention` | Scheduled intervention that alters rules | `start`, `end`, `target`, `action` | Mandates, lockdowns, media campaigns |
| `CommunityCoupling` | Couples behavior by community membership | `community_field`, `intra`, `inter` | Assortative influence and compartmentalization |

## 8. Builder-Only Utility Blocks

Some blocks are not model dynamics themselves, but they make the builder usable for complex models.

| Block | Purpose |
| --- | --- |
| `SeedSelection` | Choose specific nodes, percentages, or attribute-based seeds |
| `NodeRoleAssignment` | Mark nodes as zealots, media, leaders, hubs, or monitors |
| `AttributeInitializer` | Initialize graph/node attributes from distributions |
| `GraphImport` | Load attributes or metadata from file or dataset |
| `CommunityAssignment` | Assign communities deterministically or via detected partitions |
| `RuleAlias` | Provide human-readable aliases for deeply nested rule trees |
| `PreviewObservable` | Define what the network panel or plots should render |
| `ValidationHint` | Show expected units, ranges, and dependencies in the inspector |

## 9. NDQL Language Features Needed for Maximum Flexibility

The following language features would make NDQL suitable for complex epidemic and opinion models.

### 9.1 Typed Declarations

- `DECLARE STATUS`
- `DECLARE VARIABLE`
- `DECLARE PARAM`
- `DECLARE EDGE_VARIABLE`
- `DECLARE GLOBAL`

Each declaration should include:

- scope
- type
- range
- default
- optionality
- validation rules

### 9.2 Typed Initializers

Initialization should support:

- scalar assignment
- bounded distributions
- clipped or truncated distributions
- weighted sampling
- attribute-based seeding
- community-based seeding
- seed lists and percentage allocations

### 9.3 Expression-Based Updates

NDQL should support expressions such as:

- arithmetic updates
- min/max/clamp
- neighborhood aggregation
- conditional branches
- function calls
- stochastic draws

Examples:

```ndql
UPDATE opinion = clamp(opinion + mu * (neighbor_mean - opinion), 0, 1)
UPDATE status = IF random() < beta THEN Infected ELSE Susceptible
UPDATE media = weighted_choice(media_opinions, bias=gamma)
```

### 9.4 Selector and Guard Syntax

The language should allow:

- node selectors
- neighbor selectors
- edge selectors
- community selectors
- attribute selectors
- opinion-distance selectors
- temporal selectors

Example:

```ndql
SELECT neighbor WHERE abs(opinion - neighbor.opinion) < epsilon
```

### 9.5 Composition and Nesting

Complex models often require nested decisions.

NDQL should support:

- `IF / THEN / ELSE`
- nested `BLOCK` composition
- chained conditions
- weighted branches
- fallback branches

### 9.6 Observability and Export

NDQL should let the model describe observables explicitly:

- trend plots
- prevalence plots
- phase-space plots
- opinion histograms
- opinion trajectories
- node-coloring rules

This is especially important for continuous opinions because the raw status sequence is not enough.

## 10. Recommended Implementation Order

If this catalog is implemented incrementally, the most useful order is:

1. typed variable and parameter declarations
2. opinion initialization and opinion update blocks
3. epidemic coupling and selection blocks
4. media and zealot blocks
5. hybrid coupling blocks
6. richer selectors, expressions, and nested compositions
7. observables and export directives

## 11. Practical Notes

- Keep old NDQL valid.
- Prefer block names that map clearly to one semantic responsibility.
- Do not overload generic compartments when a domain-specific block is needed.
- Make the NDQL syntax descriptive enough that a human can read a script and understand the model without opening the builder.
- Keep the builder palette filtered by model family, but allow an advanced mode where all blocks are available.

## 12. Summary

The current builder can be extended into a flexible modeling system if it grows from a small set of generic compartments into a typed block library.

For epidemics, the main missing blocks are hazard, latency, recovery, immunity, intervention, and dynamic-contact blocks.

For opinion dynamics, the main missing blocks are initialization distributions, bounded-confidence filters, biased selection, compromise kernels, stubbornness, zealots, noise, quantization, and media influence.

For coupled models, the main missing pieces are coupling blocks that can link epidemic and opinion states in both directions.

If NDQL adopts typed declarations, typed initializers, expression-based updates, and explicit observables, it will be able to describe much more complex models without sacrificing readability or backward compatibility.
