# Visual Model Builder Extension Guide

This document describes how to extend the current dashboard visual model builder so it can express epidemic models that also carry opinion variables, both continuous and discrete.

The goal is not to implement the feature now. This is a design and execution guide for a future iteration.

## 1. Scope

The current builder already supports a graph-based composition workflow for custom models. The next step is to make it capable of building models where each node may carry:

- epidemic status information
- a continuous opinion value
- a discrete opinion label
- optional coupling rules between epidemic and opinion dynamics

The builder should stay usable for simple models. Users creating a standard epidemic model should not be forced to configure opinion-specific blocks unless they need them.

## 2. Target Model Families

The extended builder should support at least these model patterns:

- epidemic models with no opinion variable
- epidemic models with a continuous opinion variable
- epidemic models with a discrete opinion variable
- epidemic models where epidemic transitions depend on opinion state
- epidemic models where opinion updates depend on infection or recovery state

This should cover the common use cases behind models such as:

- continuous opinion epidemics
- label-based opinion epidemics
- coupled opinion and infection dynamics
- models that use opinion to modulate transmission or recovery

## 3. NDQL Language Extensions

The current NDQL representation is centered on statuses, compartments, rules, and initialization. To support opinion variables, NDQL needs a typed state section and a richer initialization syntax.

### 3.1 Variable Declarations

Add explicit declarations for node state variables:

```ndql
MODEL MyModel

STATUS Susceptible
STATUS Infected

VARIABLE opinion TYPE continuous RANGE [0,1]
VARIABLE label TYPE discrete VALUES [A,B,C]
```

Suggested semantics:

- `continuous` values are numeric and may evolve by arithmetic or bounded updates
- `discrete` values are categorical labels and may evolve by assignment or switching rules
- variables may be optional and can coexist with epidemic statuses

### 3.2 Initialization

Initialization should be able to assign either scalar values or distributions.

Examples:

```ndql
INITIALIZE
SET Susceptible 0.95
SET Infected 0.05
SET opinion UNIFORM 0.0 1.0
SET label SAMPLE [A,B,C] WEIGHTS [0.5,0.3,0.2]
```

Recommended additions:

- `SET <variable> <scalar>` for fixed values
- `SET <variable> UNIFORM <min> <max>` for continuous random initialization
- `SET <variable> NORMAL <mean> <std>` if bounded or clipped by variable range
- `SET <variable> SAMPLE [..] WEIGHTS [..]` for discrete variables
- `SET <variable> FROM NODE_ATTRIBUTE <attr>` if the graph already contains the data

### 3.3 Update Rules

Current `RULE` blocks are sufficient for status transitions, but opinion variables need variable-aware updates.

Extend the syntax to support:

```ndql
RULE
FROM Susceptible
TO Infected
USING threshold_rule
WHEN opinion > 0.7

UPDATE opinion = opinion + 0.1
UPDATE label = "B"
```

The new rule layer should support:

- conditional transitions
- continuous updates with clamping
- discrete reassignment
- simultaneous updates to status and opinion variables

### 3.4 Parameter Typing

NDQL parameters should carry type metadata so the runtime can validate values:

- `int`
- `float`
- `bool`
- `string`
- `enum`
- `range`
- `distribution`

This matters because the builder needs to distinguish:

- threshold parameters that should remain floats in `[0,1]`
- counters that must be integers
- opinion values that may be scalar floats or categorical labels

### 3.5 Backward Compatibility

The extended NDQL must remain valid for existing models.

Compatibility rules:

- old scripts without `VARIABLE` or `UPDATE` blocks remain valid
- status-only epidemic models continue to compile as before
- opinion-related syntax should be optional and non-breaking

## 4. Builder Blocks to Add

The interface should remain block-based, but the block palette needs a second layer for state variables and opinion dynamics.

### 4.1 Variable Blocks

Add blocks for node-level variables:

- `Continuous Opinion`
- `Discrete Opinion`
- `Opinion Distribution`
- `Node Attribute Source`

Suggested configuration fields:

- variable name
- type
- default value or initialization mode
- valid range or label set
- visualization mode

### 4.2 Opinion Update Blocks

Add blocks for dynamics on those variables:

- `Continuous Update`
- `Discrete Switch`
- `Bounded Drift`
- `Consensus Pull`
- `Noisy Update`
- `Neighbor Influence`

Suggested configuration fields:

- target variable
- update operator
- coefficients or weights
- neighborhood sampling strategy
- clamping / normalization behavior

### 4.3 Coupling Blocks

Add blocks that connect epidemic and opinion dynamics:

- `Opinion Affects Infection`
- `Opinion Affects Recovery`
- `Infection Affects Opinion`
- `Status-Dependent Opinion Update`
- `Opinion-Dependent Contact Rate`

These blocks are needed because many useful models are not pure epidemic or pure opinion systems. They are coupled systems.

### 4.4 Initialization Blocks

The builder should support explicit initialization blocks for:

- epidemic status ratios
- continuous opinion ranges
- discrete opinion label probabilities
- per-node attribute seeding from loaded graphs

## 5. Interface Extensions

The interface should be extended in a way that keeps the current visual model builder recognizable.

### 5.1 Separate Tabs or Modes

Introduce a clear split between:

- epidemic structure
- opinion structure
- coupling rules
- NDQL preview

A single canvas can still be used, but the left palette and the right inspector should change with the active mode.

### 5.2 Typed Node Appearance

The canvas should visually distinguish block types:

- epidemic status nodes
- continuous opinion blocks
- discrete opinion blocks
- coupling blocks

Recommended cues:

- color family by type
- icon shape by function
- solid border for state variables
- dashed border for coupling or derived blocks

### 5.3 Typed Properties Panel

The properties editor should adapt to the selected block.

Examples:

- a continuous opinion block shows numeric range, step size, and clipping
- a discrete opinion block shows label list and weights
- a coupling block shows source variable, target variable, and influence strength

### 5.4 Validation Feedback

The builder should validate before save:

- every referenced variable exists
- continuous opinion values have numeric ranges
- discrete labels are defined before use
- couplings do not reference missing blocks
- incompatible blocks are flagged early

Validation errors should be shown inline on the canvas and in the save dialog.

### 5.5 NDQL Preview

The NDQL preview should highlight typed sections:

- status declarations
- variable declarations
- coupling rules
- initialization

This makes the language understandable even when the model becomes more expressive.

## 6. Data Model Extensions

The JSON payload produced by the builder will need new fields beyond the current `statuses`, `compartments`, `rules`, and `initial_status`.

Recommended additions:

- `variables`
- `updates`
- `couplings`
- `initial_variables`
- `schema_version`

Example shape:

```json
{
  "name": "CoupledOpinionEpidemic",
  "statuses": [],
  "variables": [
    { "name": "opinion", "type": "continuous", "range": [0, 1] },
    { "name": "label", "type": "discrete", "values": ["A", "B", "C"] }
  ],
  "updates": [],
  "couplings": [],
  "initial_status": [],
  "initial_variables": []
}
```

The version field is important so the backend can evolve without breaking older saved models.

## 7. Phased Implementation Plan

Implement this incrementally. Each phase should deliver a usable improvement on its own.

### Phase 1: Typed State Foundation

Goal:

- introduce typed variable declarations in the NDQL schema
- add builder support for one continuous opinion variable and one discrete opinion variable per model
- preserve full backward compatibility with existing custom models

Success criteria:

- a saved model can declare an opinion variable explicitly
- the generated NDQL can round-trip through save and reload
- existing epidemic-only models still save and run unchanged

### Phase 2: Initialization and Validation

Goal:

- support initialization for continuous and discrete opinion variables
- add strong validation for ranges, labels, and required references
- surface errors in the UI before saving

Success criteria:

- users can seed opinion values from constants, ranges, or discrete distributions
- invalid ranges or missing labels are rejected with clear messages
- no model can be saved with an unresolved reference

### Phase 3: Opinion Update Blocks

Goal:

- add blocks for continuous drift, discrete switching, and neighbor influence
- translate those blocks into NDQL update syntax

Success criteria:

- the builder can express at least one continuous opinion update rule
- the builder can express at least one discrete opinion transition rule
- generated scripts are readable and deterministic

### Phase 4: Coupled Epidemic-Opinion Dynamics

Goal:

- allow opinion state to affect epidemic transitions
- allow epidemic state to affect opinion updates
- support mixed models without forcing users into hidden conventions

Success criteria:

- one model can combine epidemic and opinion variables in the same payload
- the runtime can execute a coupled model without manual edits
- the UI makes the coupling visible in the graph and in the preview

### Phase 5: UX Hardening

Goal:

- refine block palette layout
- improve labels and helper text
- add type-aware styling and validation hints
- improve NDQL readability

Success criteria:

- users can create a coupled model without needing documentation open beside the app
- the builder remains usable on smaller screens
- new users can distinguish epidemic blocks from opinion blocks quickly

## 8. Recommended Acceptance Checklist

Before the feature is considered complete, the following should be true:

- the builder can create an epidemic model with continuous opinion variables
- the builder can create an epidemic model with discrete opinion variables
- the NDQL syntax can represent both cases clearly
- the UI shows the correct block palette and property panel for the selected type
- saved models reload with the same structure and metadata
- old models continue to work without migration

## 9. Notes on Usability

This feature will be easier to adopt if the UI avoids exposing too many advanced options at once.

Practical design rules:

- default to a simple epidemic builder view
- reveal opinion-specific blocks only when needed
- keep continuous and discrete opinion workflows visually distinct
- use helper text that explains the model behavior, not just the field name

## 10. Suggested Deliverable Order

If this work is split among multiple contributors, a practical order is:

1. extend the model schema and NDQL parser/serializer
2. add opinion variable blocks and validation
3. add update and coupling blocks
4. refine the UI and preview
5. add tests and migration coverage

That ordering minimizes the risk of building a UI that cannot be serialized or executed.

## 11. Current Shipped Behavior

The dashboard implementation already includes a first, bounded version of this design:

- the builder is split into use cases and filters the available blocks accordingly
- starter templates are provided for epidemic, continuous-opinion, discrete-opinion, and coupled layouts
- the builder can export both NDQL text and generated Python source
- custom opinion starters initialize their own status ratios directly, so they do not require an epidemic `Infected` class

Future work should extend this foundation without reintroducing epidemic-only assumptions into opinion workflows.
