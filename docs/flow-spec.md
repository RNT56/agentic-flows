# Flow spec

The current spec version is `agentic-flows/v1`.

## Required top-level fields

- `spec_version`: Schema generation. Current value is `agentic-flows/v1`.
- `id`: Stable flow identifier, such as `coding.feature-implementation`.
- `version`: Flow version in semantic version format.
- `title`: Human-readable flow name.
- `summary`: Short purpose statement.
- `stability`: `experimental`, `preview`, or `stable`.
- `deprecated_by`: Optional replacement flow id when this flow is deprecated.
- `migration`: Optional migration summary and steps. Required when `deprecated_by` is set.
- `owners`: People or teams responsible for the flow.
- `tags`: Search and grouping terms.
- `entrypoint`: First node id.
- `runtime`: Supported cores and required runtime capabilities.
- `contracts`: Inputs, outputs, and artifacts.
- `nodes`: Execution graph nodes.
- `edges`: Directed graph edges.
- `quality_gates`: Completion criteria.
- `observability`: Expected event names and metrics.

## Node types

- `intake`: Captures the task, context, and constraints.
- `plan`: Produces a strategy before work starts.
- `agent_task`: Work performed by an agent or worker.
- `tool`: Tool or command execution.
- `verifier`: Independent validation.
- `approval`: Human or policy decision.
- `decision`: Automated branch decision.
- `handoff`: Transfer to another worker, lane, or core.
- `finalizer`: Closeout and result packaging.

## Quality gates

Every flow must include at least one required quality gate.

Use `evidence` for human-readable guidance. Use `evidence_refs` for machine-readable references to declared `contracts.artifacts` entries or `observability.events` names.

Gate types:

- `command`: A command or check the runtime should run or translate.
- `review`: Human or verifier review.
- `artifact`: Required output artifact.
- `policy`: Runtime policy check.

## Semantic validation

`flowctl validate` checks more than the JSON Schema:

- Node ids are unique.
- The entrypoint exists.
- Edge targets exist.
- Every node is reachable from the entrypoint.
- At least one quality gate is required.
- Command gates include a command.
- Required quality gates include `evidence_refs`.
- Quality gate `evidence_refs` point to declared artifacts or events.
- Deprecated flows include migration guidance.

## Event validation

`flowctl validate-event` checks event JSON against `schemas/event.schema.json`.

It also applies semantic timestamp validation so event examples and run artifacts fail when `timestamp` is not an RFC 3339 date-time.

## Run validation

`flowctl validate-run` checks completed run bundles against `schemas/run.schema.json`, the event schema, and the source flow.

It verifies:

- run metadata matches event metadata
- the referenced source flow exists and validates
- event names are declared by the source flow
- node ids reference source flow nodes
- completed runs include `flow.completed`
- completed runs include required outputs
- every required quality gate has passed `gate.completed` evidence
- passed gate evidence ids or kinds match the source gate's `evidence_refs`

`flowctl replay` validates a run bundle and reconstructs a timeline with run status, outputs, passed gates, evidence refs, and ordered events.

## Sample validation

`flowctl validate-samples` checks `*.sample.json` files under `examples/samples/`.

It verifies:

- the referenced source flow exists and validates
- sample flow id and version match the source flow
- all required inputs are present
- all required expected outputs are present
- unknown input or output ids are rejected
- sample values match the declared contract field types
- every production flow under `flows/` has a sample when the command is run with default paths
