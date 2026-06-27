# Event streams

Event streams validate a run from separate event files instead of a single run bundle.

They are validated by:

```bash
flowctl validate-stream examples/streams/
```

## Purpose

Use an event stream when a runtime stores events individually but still needs to prove that the run matches a source flow.

A stream manifest connects:

- the source `flow.yaml`
- run metadata
- required outputs for completed runs
- ordered event file paths

## File naming

Use:

```text
examples/streams/<flow-or-scenario>/<scenario>.stream.json
```

Put event files under the stream folder, usually:

```text
examples/streams/<flow-or-scenario>/events/*.json
```

## Required structure

Every stream manifest must include:

- `event_stream_version`
- `flow.id`
- `flow.version`
- `flow.source`
- `run.id`
- `run.core`
- `run.status`
- `run.started_at`
- `events`

Completed streams must also include:

- `run.completed_at`
- all required flow outputs
- a `flow.completed` event
- passed `gate.completed` events for every required quality gate
- evidence ids or kinds matching the source flow's gate `evidence_refs`

## Validation rules

`flowctl validate-stream` checks:

- stream schema validity
- source flow existence and validity
- flow id and version match the source flow
- run core is declared in `runtime.supported_cores`
- referenced event files exist and parse as event JSON
- event schema validity
- event flow id, flow version, run id, and core match the stream
- event node ids exist in the source flow
- event names are declared in the source flow
- required outputs exist for completed streams
- required quality gates have passed evidence
- passed gate evidence matches the gate's declared `evidence_refs`
