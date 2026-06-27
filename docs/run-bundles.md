# Run bundles

Run bundles are evidence packages for completed or attempted flow runs.

They are validated by:

```bash
flowctl validate-run examples/runs/
```

## Purpose

A run bundle connects four things:

- the source `flow.yaml`
- the run metadata
- the emitted event stream
- the artifacts and outputs used as evidence

This lets an independent consuming project prove that it completed a flow without requiring this repository to become the runtime.

## File naming

Use:

```text
<flow-or-scenario>.run.json
```

Examples:

- `feature-implementation.run.json`
- `human-review-approved.run.json`
- `multi-agent-supervisor-smoke.run.json`

## Required structure

Every run bundle must include:

- `run_version`
- `flow.id`
- `flow.version`
- `flow.source`
- `run.id`
- `run.core`
- `run.status`
- `run.started_at`
- `events`

Completed runs must also include:

- `run.completed_at`
- all required flow outputs
- a `flow.completed` event
- passed `gate.completed` events for every required quality gate
- evidence for required gates

## Validation rules

`flowctl validate-run` checks:

- run schema validity
- source flow existence and validity
- flow id and version match the source flow
- run core is declared in `runtime.supported_cores`
- event schema validity
- event flow id, flow version, run id, and core match the run
- event node ids exist in the source flow
- event names are declared in the source flow
- required outputs exist for completed runs
- required quality gates have passed evidence

## Independent consumer usage

ThinClaw, NilCore, CrustCore, or another project can emit run bundles if they choose to consume `agentic-flows`.

That does not require shared runtime state. The bundle is the exchange format.

