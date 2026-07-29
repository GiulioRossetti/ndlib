# NDQL User Manual

This manual explains the NDQL dialect emitted by the NDlib visual model builder and accepted by the dashboard parser.

The goal of NDQL is practical readability:

- keep model definitions line-oriented
- preserve backward compatibility with the classic `STATUS / COMPARTMENT / RULE / INITIALIZE` format
- make epidemic and opinion dynamics explicit
- allow the builder to round-trip through save, reload, parse, and Python generation

If you only need the block catalog, see [Network Builder and NDQL Block Catalog](network_builder_ndql_block_catalog.md).

## 1. What NDQL Is For

NDQL is meant to describe:

- epidemic models with explicit status transitions
- continuous opinion models with bounded values in `[0,1]`
- discrete opinion models with class percentages
- coupled epidemic-opinion systems
- custom builder-generated models with typed declarations and observables

It is not intended to replace the Python API. It is the text form of the dashboard model builder.

## 2. Core Ideas

NDQL has five main kinds of statements:

- `MODEL` names the model
- `TYPE` declares the model family
- `DECLARE` introduces typed parameters, variables, or globals
- `STATUS`, `BIN`, `BLOCK`, `COMPARTMENT`, `RULE`, `UPDATE`, `OBSERVE`, `INITIALIZE` define the model behavior
- `WHEN` and `SCHEDULE` optionally gate updates over conditions and time

Classic epidemic scripts remain valid. Continuous-opinion scripts now also support typed initialization and explicit update directives.

## 3. Syntax Summary

### 3.1 Model Header

```ndql
MODEL MyModel
TYPE EPIDEMIC
```

Supported types used by the builder are:

- `EPIDEMIC`
- `CONTINUOUS_OPINION`
- `COUPLED`

The dashboard may omit `TYPE` for classic epidemic scripts, but the typed form is preferred for builder round-trips.

### 3.2 Declarations

Use `DECLARE` to define typed data:

```ndql
DECLARE PARAM beta TYPE float DEFAULT 0.1
DECLARE PARAM gamma TYPE float DEFAULT 0.05
DECLARE VARIABLE opinion TYPE continuous RANGE [0,1]
DECLARE GLOBAL simulation_name TYPE string DEFAULT DemoRun
DECLARE EDGE_VARIABLE edge_weight TYPE float DEFAULT 1.0
```

Common declaration kinds:

- `PARAM`
- `GLOBAL`
- `VARIABLE`
- `EDGE_VARIABLE`
- `STATUS`
- `BIN`

Rules of thumb:

- `PARAM` is for model parameters used in rules and blocks
- `GLOBAL` is for model-wide metadata or shared control values
- `VARIABLE` is for node, edge, or graph state
- `EDGE_VARIABLE` is for edge-level data
- `STATUS` and `BIN` are mostly compatibility aliases for the builder

### 3.3 Initialization

Initialization assigns starting values:

```ndql
INITIALIZE
SET Susceptible 0.95
SET Infected 0.05
SET INITIAL_OPINION_DISTRIBUTION bimodal
```

The current builder emits:

- status allocation ratios for epidemic models
- initial opinion distribution selectors for continuous-opinion models

Supported opinion distributions include:

- `uniform`
- `normal`
- `gaussian`
- `bimodal`
- `left_skewed`
- `right_skewed`
- `polarized`

The builder interprets these as bounded distributions in `[0,1]`.

### 3.4 Blocks and Compartments

NDQL still accepts the classic syntax:

```ndql
STATUS Susceptible
STATUS Infected

COMPARTMENT infection
TYPE NodeStochastic
PARAM rate 0.1
TRIGGER Infected
```

The richer typed form uses `BLOCK` for opinion and utility components:

```ndql
BLOCK bounded_confidence
TYPE OpinionDistanceThreshold
PARAM epsilon 0.1
```

The builder uses `STATUS`, `COMPARTMENT`, and `BLOCK` depending on the family and the legacy compatibility path.

### 3.5 Rules

Classic transition rules remain:

```ndql
RULE
FROM Susceptible
TO Infected
USING infection
```

For composed blocks:

```ndql
IF c1 THEN c2 ELSE c3 AS r1
```

### 3.6 Update Directives

Continuous-opinion models and advanced builder models can use explicit updates:

```ndql
WHEN iteration >= 0
SCHEDULE 0 10 PERIOD 1 PHASE 0
UPDATE opinion = clamp(opinion + mu * (neighbor_mean - opinion), 0, 1)
```

Semantics:

- `WHEN` is a boolean guard
- `SCHEDULE` constrains execution to a time window
- `UPDATE` assigns or mutates a target variable

The current parser and dashboard serializer support these directives for continuous-opinion round-trips.

### 3.7 Observables

Observables describe what should be plotted or exported:

```ndql
OBSERVE opinion AS bins BINS 20 RANGE [0,1]
OBSERVE prevalence AS line
```

They are used by the builder to make the network and plot tabs explicit rather than inferred.

## 4. Family-Specific Usage

### 4.1 Epidemic Models

Use epidemic NDQL when the main state is a compartment label.

Minimal example:

```ndql
MODEL SIRExample

STATUS Susceptible
STATUS Infected
STATUS Recovered

COMPARTMENT infection
TYPE NodeStochastic
PARAM rate 0.05
TRIGGER Infected

COMPARTMENT recovery
TYPE NodeStochastic
PARAM rate 0.1

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
```

Builder-generated epidemic models may also include:

- `NodeThreshold`
- `EdgeStochastic`
- `CountDown`
- `NodeCategoricalAttribute`
- `NodeNumericalAttribute`
- `Compose`
- `Schedule`
- `Observe`

### 4.2 Continuous Opinion Models

Use continuous-opinion NDQL when each node carries a bounded opinion value.

Minimal example:

```ndql
MODEL OpinionExample
TYPE CONTINUOUS_OPINION
INITIAL_OPINION_DISTRIBUTION bimodal

BIN LowOpinion
BIN HighOpinion

BLOCK bounded_confidence
TYPE OpinionDistanceThreshold
PARAM epsilon 0.2

BLOCK selection_bias
TYPE OpinionSelectionBias
PARAM gamma 1.5

BLOCK opinion_compromise
TYPE OpinionCompromise
PARAM mu 0.5

BLOCK opinion_normalization
TYPE OpinionNormalization
PARAM min 0.0
PARAM max 1.0

INITIALIZE
SET LowOpinion 0.5
SET HighOpinion 0.5
```

Typical opinion blocks:

- `OpinionDistanceThreshold`
- `OpinionSelectionBias`
- `OpinionCompromise`
- `OpinionStubbornness`
- `OpinionNoise`
- `OpinionPolarization`
- `OpinionExternalField`
- `OpinionTrustFilter`
- `OpinionMemory`
- `OpinionNormalization`
- `OpinionQuantization`
- `OpinionMediaInfluence`
- `OpinionZealot`

### 4.3 Discrete Opinion Models

Use discrete-opinion NDQL when the opinion is categorical.

Example:

```ndql
MODEL MajorityRuleExample

STATUS Agree
STATUS Disagree

COMPARTMENT adopt_agree
TYPE NodeThreshold
PARAM threshold 0.5
TRIGGER Agree

COMPARTMENT adopt_disagree
TYPE NodeThreshold
PARAM threshold 0.5
TRIGGER Disagree

RULE
FROM Disagree
TO Agree
USING adopt_agree

RULE
FROM Agree
TO Disagree
USING adopt_disagree

INITIALIZE
SET Agree 0.5
SET Disagree 0.5
```

For discrete opinion models, the dashboard supports initial class percentages directly.

### 4.4 Coupled Models

Use coupled NDQL when epidemic and opinion state interact.

Example:

```ndql
MODEL CoupledExample
TYPE COUPLED

DECLARE VARIABLE opinion TYPE continuous RANGE [0,1]

STATUS Susceptible
STATUS Infected
STATUS Recovered

COMPARTMENT opinion_gate
TYPE NodeNumericalVariable
PARAM var opinion
PARAM var_type ATTRIBUTE
PARAM op >=
PARAM value 0.4
PARAM probability 1.0

COMPARTMENT infection
TYPE NodeStochastic
PARAM rate 0.05
TRIGGER Infected

COMPARTMENT recovery
TYPE NodeStochastic
PARAM rate 0.08

COMPARTMENT coupling
TYPE ConditionalComposition
PARAM condition opinion_gate
PARAM first_branch infection
PARAM second_branch recovery

RULE
FROM Susceptible
TO Infected
USING coupling

INITIALIZE
SET Susceptible 0.9
SET Infected 0.1
SET Recovered 0.0
```

## 5. Block Families

### 5.1 Core Blocks

These blocks are shared across epidemic and opinion models:

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

Practical uses:

- `Selector` chooses nodes, neighbors, or media
- `Filter` restricts eligible candidates
- `Kernel` or `Transform` performs the actual update
- `Schedule` activates rules in time windows
- `Observe` defines what gets plotted

### 5.2 Epidemic Blocks

The builder currently exposes epidemic blocks for:

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

### 5.3 Opinion Blocks

The opinion family includes:

- `OpinionDistribution`
- `OpinionDistanceThreshold`
- `OpinionSelectionBias`
- `OpinionCompromise`
- `OpinionStubbornness`
- `OpinionNoise`
- `OpinionPolarization`
- `OpinionExternalField`
- `OpinionTrustFilter`
- `OpinionMemory`
- `OpinionNormalization`
- `OpinionQuantization`
- `OpinionMediaInfluence`
- `OpinionZealot`
- `OpinionConsensusBlock`
- `OpinionRepulsion`
- `OpinionAssimilation`
- `OpinionMultiTopic`
- `OpinionLabelSwitch`
- `OpinionBoundedDrift`

### 5.4 Hybrid Blocks

Hybrid blocks connect epidemic and opinion state:

- `OpinionAffectsInfection`
- `OpinionAffectsRecovery`
- `OpinionAffectsContactRate`
- `InfectionAffectsOpinion`
- `StatusDependentOpinionUpdate`
- `EpidemicDependentBias`
- `AttributeCoupling`
- `PolicyIntervention`
- `CommunityCoupling`

## 6. Builder Mapping

The visual builder maps directly to NDQL:

- status cards become `STATUS` statements
- compartment cards become `COMPARTMENT` or `BLOCK` statements
- declaration rows become `DECLARE` statements
- observables become `OBSERVE` statements
- update rows become `WHEN / SCHEDULE / UPDATE` directives
- initial status controls become `INITIALIZE` lines

The builder keeps a live NDQL preview so the script is always visible before save.

## 7. Compatibility Rules

The parser is intentionally permissive:

- classic epidemic scripts remain valid
- `STATUS` remains valid even if typed declarations are used elsewhere
- `COMPARTMENT` remains valid alongside `BLOCK`
- `IF ... THEN ... ELSE ... AS ...` still works as shorthand for composition
- update directives are optional and only used where supported

This allows older NDQL files to continue working while the builder emits richer scripts for newer models.

## 8. Worked Examples

### 8.1 Minimal Epidemic Example

```ndql
MODEL MiniSIR

STATUS Susceptible
STATUS Infected

COMPARTMENT infection
TYPE NodeStochastic
PARAM rate 0.1
TRIGGER Infected

RULE
FROM Susceptible
TO Infected
USING infection

INITIALIZE
SET Susceptible 0.9
SET Infected 0.1
```

### 8.2 Minimal Continuous Opinion Example

```ndql
MODEL MiniOpinion
TYPE CONTINUOUS_OPINION
INITIAL_OPINION_DISTRIBUTION uniform

BIN LowOpinion
BIN HighOpinion

BLOCK opinion_normalization
TYPE OpinionNormalization
PARAM min 0.0
PARAM max 1.0

INITIALIZE
SET LowOpinion 0.5
SET HighOpinion 0.5
```

### 8.3 Continuous Opinion With Updates

```ndql
MODEL OpinionUpdateExample
TYPE CONTINUOUS_OPINION
INITIAL_OPINION_DISTRIBUTION gaussian

BIN LowOpinion
BIN HighOpinion

BLOCK compromise
TYPE OpinionCompromise
PARAM mu 0.5

WHEN iteration >= 0
SCHEDULE 0 100 PERIOD 1 PHASE 0
UPDATE opinion = clamp(opinion + mu * (neighbor_mean - opinion), 0, 1)
```

### 8.4 Coupled Example

```ndql
MODEL CoupledPolicyExample
TYPE COUPLED

DECLARE PARAM epsilon TYPE float DEFAULT 0.2
DECLARE PARAM gamma TYPE float DEFAULT 1.5
DECLARE VARIABLE opinion TYPE continuous RANGE [0,1]

STATUS Susceptible
STATUS Infected
STATUS Recovered

BLOCK trust_filter
TYPE OpinionTrustFilter
PARAM trust_threshold 0.25

BLOCK policy
TYPE PolicyIntervention
PARAM start 20
PARAM end 40
PARAM target contact_rate
PARAM action set
PARAM value 0.5

INITIALIZE
SET Susceptible 0.94
SET Infected 0.06
SET Recovered 0.0
SET INITIAL_OPINION_DISTRIBUTION bimodal
```

### 8.5 Invalid Example

```ndql
MODEL BadExample
TYPE CONTINUOUS_OPINION

BLOCK compromise
TYPE OpinionCompromise
PARAM mu 2.0
```

Expected issue:

- `mu` should be in `[0,1]`
- the builder and parser should clamp or reject the value depending on the runtime path

## 9. Builder Round-Trip Tips

When building models in the dashboard:

1. choose the correct use case first
2. load a starter template if possible
3. edit declarations before adding complex rules
4. keep opinion variables bounded in `[0,1]`
5. use observables to make plots explicit
6. verify the live NDQL preview before saving
7. reload the saved custom model to confirm round-trip behavior

## 10. Troubleshooting

### 10.1 My continuous-opinion model starts with the wrong opinion values

Check:

- `INITIAL_OPINION_DISTRIBUTION`
- the chosen distribution family
- whether the model is actually in `CONTINUOUS_OPINION` mode

### 10.2 My opinion histogram is flat or missing

Check:

- that the model declares an opinion observable
- that the opinion values are still being written to node attributes
- that the graph is not too large for network rendering

### 10.3 My zealot nodes are not immutable

Check:

- `OpinionZealot` parameters
- whether the selected model family supports zealots
- whether a later update block overwrites the opinion again

### 10.4 My media model ignores the number of media sources

Check:

- `OpinionMediaInfluence`
- `PARAM k`
- `PARAM media_opinions`

The media count is an integer because it represents how many media sources exist.

### 10.5 My update directives do nothing

Check:

- that the parser loaded `WHEN`, `SCHEDULE`, and `UPDATE`
- that the condition is valid
- that the schedule window includes the current iteration
- that the target variable exists in the model state

## 11. Summary

NDQL is now intended to be readable by humans and executable by the dashboard:

- epidemics keep their familiar transition syntax
- continuous opinions gain explicit initialization and update directives
- discrete opinion models can specify class percentages
- coupled models can mix epidemic and opinion blocks
- observables make visual output explicit rather than inferred

That combination is what makes the builder usable for both simple models and more complex coupled pipelines.
