# Network Builder and NDQL Implementation Backlog

This backlog is derived from the phase audit in
[network_builder_ndql_phase_audit.md](/Users/rossetti/PycharmProjects/ndlib/docs/network_builder_ndql_phase_audit.md).

Current status:

- `P0` shared schema and validation work has been implemented in the backend
- `P1` canonical epidemic starter has been implemented
- `P2` remains as follow-on backlog

Priority key:

- `P0`: correctness and shared infrastructure
- `P1`: end-to-end coverage and representative model completeness
- `P2`: UI polish and broader verification

## P0 - Shared Schema and Validation

Goal: make the block metadata and payload validation explicit so the dashboard, parser, and generators share one source of truth.

Tasks:

- add a centralized block schema registry for all supported block families - `done`
- expose the registry from the dashboard backend for future UI consumption - `done`
- validate custom model payloads before save - `done`
- validate known parameter families such as continuous-opinion initialization, media counts, and zealot configuration - `done`
- keep the backend validator permissive enough to preserve legacy NDQL compatibility - `done`

Acceptance criteria:

- invalid block types are rejected before save - `done`
- invalid parameter combinations surface a readable error - `done`
- known parameter defaults can be inspected from a single registry - `done`
- the registry is reusable by dashboard, parser, and generator code - `done`

## P1 - Canonical Epidemic Coverage

Goal: prove that the later epidemic block families work as a single pipeline, not just as isolated unit tests.

Tasks:

- add one canonical late-stage epidemic starter/example - `done`
- round-trip the example through save, reload, parse, and generated Python - `done`
- verify that the full epidemic block stack remains executable together - `done`
- document the starter in the user manual and block catalog if needed - `done`

Acceptance criteria:

- one realistic epidemic model can be built without manual JSON edits - `done`
- the example survives round-trip execution - `done`
- the example demonstrates the intended block composition order - `done`

## P2 - Dashboard Inspector and UX Refinement

Goal: remove generic fallbacks where a better typed control is available and keep the builder understandable for large models.

Tasks:

- replace generic inspector inputs with typed controls for known parameters
- align dashboard defaults with backend defaults from the schema registry
- keep the opinion distribution and network graph panels consistent across families
- verify the builder on narrow and large layouts
- reduce reliance on hand-maintained palette lists over time

Acceptance criteria:

- the inspector reflects the schema rather than duplicating ad hoc defaults
- the live NDQL preview remains stable across all supported families
- opinion and network visualizations stay synchronized after simulation

## Immediate Next Step

Implement `P0` first. Once the registry and save-time validation are in place, use that same schema to drive the epidemic starter coverage and then the remaining inspector cleanup.
