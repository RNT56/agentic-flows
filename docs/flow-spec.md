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

## Node substance fields

Beyond `id`, `type`, `title`, and `description`, a node may carry the substance a consumer or the reference runner needs to actually execute it. All fields are optional and additive.

- `instructions`: The operational guidance for the node - what to do, what to capture, and what "done" looks like. Written so an agent or operator can act on it without external context.
- `command`: A shell command the node runs. Supports `${param.<id>}` and `${input.<id>}` substitution. A node with a `command` is executable by `flowctl run`; a node without one (typically `agent_task`, `approval`, `handoff`) needs a consumer-supplied handler.
- `parameters`: Declared, overridable knobs for the node (for example a `test_command`). Each has an `id`, a `type`, an optional `required` flag, an optional `default`, and a `description`. The runner fills unset parameters from their defaults.
- `inputs_schema` / `outputs_schema`: The typed inputs a node consumes and the typed outputs it returns, using the same field shape as `contracts`.
- `on_failure`: What to do when the node fails - `action` is one of `retry`, `abort`, `escalate`, or `skip`. `retry` honors `max_attempts`; `fallback_node` names an alternate node.

Keep substance portable. Concrete commands, parameters, and instructions belong in the flow; sandboxing, secrets, the agent model, and approval UX stay with the consumer or in `runtime.adapter_hints`. See [runnable-flows.md](runnable-flows.md) for the execution model.

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

## Event stream validation

`flowctl validate-stream` checks multi-file event stream manifests against `schemas/event-stream.schema.json`, the event schema, and the source flow.

It verifies:

- referenced event files exist
- event metadata matches stream metadata
- event names and node ids are declared by the source flow
- completed streams include required outputs
- completed streams include passed evidence for every required quality gate

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

## Running a flow

`flowctl run <flow.yaml>` executes a flow with the built-in local handlers and writes a real run bundle:

- nodes run in dependency order derived from `requires`/`produces`
- `tool` nodes and any node with a `command` run the command as a subprocess and capture stdout, stderr, and exit code as an artifact
- `intake`, `plan`, `decision`, `verifier`, and `finalizer` nodes assemble structured records from their inputs and instructions
- `agent_task`, `approval`, and `handoff` nodes without a `command` are reported as needing a consumer-supplied handler, and the run is marked incomplete
- a required gate passes only when every artifact in its `evidence_refs` was produced by a successful step
- the produced bundle is validated against `schemas/run.schema.json` before the command returns

Pass inputs with `--input id=value` and override parameters with `--param id=value`. Use `--workdir` to point command nodes at a target checkout and `--out` to choose the bundle directory (defaults to `.agentic-runs/<flow>`). See [runnable-flows.md](runnable-flows.md) for the full model.

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
