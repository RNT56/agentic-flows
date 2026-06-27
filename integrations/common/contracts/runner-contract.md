# Runner contract

An adapter is compatible with `agentic-flows/v1` when it can implement this interface in its host language.

## Load

Input:

- Path or URI to `flow.yaml`.

Required behavior:

- Parse YAML.
- Validate against `schemas/flow.schema.json`.
- Reject unsupported `spec_version`.
- Reject flows that do not list the current core in `runtime.supported_cores`.
- Reject flows that require unavailable runtime capabilities.

## Plan

Input:

- Valid flow document.
- Runtime execution context.

Required behavior:

- Build a graph from `nodes` and `edges`.
- Start at `entrypoint`.
- Preserve branch conditions for runtime decisions.
- Expose required quality gates before execution starts.

## Execute

Input:

- Planned graph.
- Flow inputs.

Required behavior:

- Record node start and completion events.
- Preserve artifacts named in `contracts.artifacts`.
- Stop or pause when an `approval` node requires operator input.
- Attach evidence to required gates.

## Complete

Input:

- Run state and gate evidence.

Required behavior:

- Reject completion if a required gate is missing.
- Emit a final `flow.completed` or failure event.
- Return outputs matching `contracts.outputs`.

