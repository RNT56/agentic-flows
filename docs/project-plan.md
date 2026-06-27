# Project plan

## Assessment of the original plan

The proposed structure was directionally right, but not complete enough to execute safely.

What was good:

- It separated reusable `flows/` from copyable `templates/`.
- It recognized ThinClaw, NilCore, and CrustCore as independent projects rather than one merged runtime.
- It included schemas, tools, tests, and integration folders.

What was missing:

- A concrete flow schema.
- A validator that can fail malformed flows in CI.
- A runtime event contract.
- Versioning rules for flow compatibility.
- A definition of ready for reusable flows.
- A clear boundary between this repo and the independent projects that may consume it.
- Starter flows that are valid today.
- CI that protects the repository from documentation-only drift.

This repo now starts from an executable contract-first baseline instead of just a folder plan.

## Product idea

`agentic-flows` is the workflow definition layer for reusable RNT56 agentic workflows.

It should answer four questions for every reusable workflow:

1. What inputs does the workflow accept?
2. Which nodes execute, verify, approve, or finalize work?
3. What quality gates prove that the workflow is complete?
4. Which capabilities must an optional consumer such as ThinClaw, NilCore, CrustCore, or a standalone runner provide?

It should not become a fourth agent runtime. Runtime execution stays in the cores.

## Stack

- YAML flow definitions for human-editable workflow specs.
- JSON Schema for machine-readable contracts.
- Python `flowctl` for validation, listing, and graph export.
- GitHub Actions for repository-level validation.
- Runtime adapter contracts in `integrations/`.

This is intentionally small. The repo can be useful immediately while Rust and Go adapters mature inside the three core projects.

## Execution roadmap

The detailed roadmap now lives in [roadmap.md](roadmap.md). The current task board lives in [tasks.md](tasks.md).

### Phase 1: Contract baseline

Status: implemented.

- Add repo structure.
- Add `schemas/flow.schema.json`, `schemas/node.schema.json`, and `schemas/event.schema.json`.
- Add `flowctl validate`, `flowctl list`, and `flowctl graph`.
- Add starter production flows and templates.
- Add CI validation.

Acceptance gate:

- `flowctl validate` and `pytest` pass locally and in CI.

### Phase 2: Runtime adapters

Implement thin adapters only inside consuming repos that choose to opt in.

- ThinClaw could load flows as durable routines and record operator decisions.
- NilCore could dispatch node execution as sandboxed worker jobs.
- CrustCore could consume verifier gates and emit patch/audit proof.

Acceptance gate:

- One flow can be loaded by each core without custom per-flow code.

### Phase 3: Execution evidence

Add run-output examples and event validation.

- Store sample event streams under `examples/`.
- Add `flowctl validate-event`.
- Add checks that required quality gates are represented in run evidence.

Acceptance gate:

- A completed run can be replayed from event JSON and mapped to the source flow.

### Phase 4: Packaging

Publish stable consumption surfaces.

- Tag schema releases.
- Publish a small package or vendorable archive if needed.
- Add changelog and compatibility matrix.

Acceptance gate:

- A consuming project can pin `agentic-flows` by tag and know whether a flow is compatible.

## Current limitations

- The repo validates definitions; it does not execute nodes.
- Optional-consumer-specific APIs are documented as contracts, not compiled adapters.
- Command gates are declarative. The consuming project decides how and where to run them.
- Cross-core compatibility should be proven with real adapters before any flow is marked `stable`.
