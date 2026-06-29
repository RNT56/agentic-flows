# Flow spec

The current spec version is `agentic-flows/v1`, with an additive superset `agentic-flows/v1.1` (sub-flow composition, evidence classes, environments, bounded loops and fan-out, and parameters). Every `v1` flow is a valid `v1.1` flow.

## Required top-level fields

- `spec_version`: Schema generation. `agentic-flows/v1` or, for flows using v1.1 primitives, `agentic-flows/v1.1`.
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
- `flow_ref`: Run another flow as a sub-step. Available under `spec_version: agentic-flows/v1.1`. See [Sub-flow composition](#sub-flow-composition).

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
- `judgment`: A recorded decision against enumerated criteria (`agentic-flows/v1.1`).
- `acceptance`: A machine-readable acceptance spec with auto and scored criteria (`agentic-flows/v1.1`).
- `probe`: A runtime probe against a provisioned environment (`agentic-flows/v1.1`).

### Reviewer identity

For a `judgment` or `acceptance` gate, the passed `gate.completed` event must carry a `payload.reviewer_id`, and that reviewer must **not** be one of the flow's producing agents (any node `agent`). This mirrors `proof.verified-patch-acceptance` — a model cannot sign off on its own work. `flowctl validate-run` rejects a missing reviewer or a self-review.

### Evidence class

Under `agentic-flows/v1.1`, a gate may declare the class of evidence that must back it:
`deterministic` < `fixture` < `sandbox-run` < `judgment` < `external-production`, ordered by how much non-repo trust each requires. Use `evidence_class` for an exact class or `evidence_class_min` for a floor. `flowctl validate-run` then requires a passed gate's evidence to carry a satisfying `evidence_class`, and rejects a `standalone` run that emits `sandbox-run` or `external-production` evidence — those require a runtime that provisioned the environment. This keeps "evidence over assertion" honest about *which kind* of evidence backed each gate.

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

## Environments and provenance

Under `agentic-flows/v1.1`, a node may declare an ephemeral `environment` the runtime provisions before the node runs and tears down after:

```yaml
- id: test
  type: tool
  title: Run unit and integration tests
  description: Provision a throwaway datastore, run the suite, tear it down.
  tool: command-runner
  environment:
    provides: [ephemeral-datastore]
    ephemeral: true
    teardown_required: true
```

This is what lets a gate produce honest `sandbox-run` evidence: the suite really ran against a real (ephemeral) resource a runtime stood up, never fabricated production state. `flowctl` enforces the provenance guardrail in `validate-run`:

- `sandbox-run` evidence requires a runtime-issued `env.provisioned` event (no provisioning, no sandbox claim).
- an `env.provisioned` event's `payload.provisioner` must **not** be one of the flow's producing agents — provenance is non-self-issued, so an authoring agent cannot mint it.
- an ephemeral environment with `teardown_required` must record a matching `env.torn_down` event.

`flowctl` checks this provenance for **consistency**; the runtime attests its **authenticity** (e.g. a signed or content-addressed bundle). This is the honest boundary of a contract layer.

## Bounded loops and fan-out

Under `agentic-flows/v1.1`, a node may declare a bounded `iteration` loop or a `fan_out` over many instances. Both carry mandatory bounds so the "execution steps are bounded" guarantee extends into loops and fan-out:

```yaml
# iterate a node until a gate passes, capped at max_iterations
iteration:
  max_iterations: 3
  until: "gate:build-and-component-tests-pass"
  on_exhausted: fail        # fail | handoff

# run one node as N bounded instances with per-instance evidence
fan_out:
  over: endpoints
  cardinality: { min: 1, max: 50 }
  aggregate: all_pass       # all_pass | threshold | any
  instance_id: endpoint
```

`flowctl validate` requires an `iteration` block to declare an integer `max_iterations` (no unbounded loops) and, when `until` is `gate:<id>`, the gate must exist; a `fan_out` block must declare a non-empty `over`, a `cardinality` with an integer `min`, and an `aggregate` rule.

## Parameters

Under `agentic-flows/v1.1`, an optional top-level `parameters` block declares typed bindings a runtime resolves before execution. Reference a parameter as `{{param.<id>}}` inside a gate `command` (or a `flow_ref` node's `with` bindings):

```yaml
parameters:
  - id: build_command
    type: text
    required: true
    description: Build command for the chosen stack.
  - id: test_command
    type: text
    required: true
    description: Test command for the chosen stack.
quality_gates:
  - id: build-and-tests-pass
    title: Build and tests pass
    type: command
    required: true
    command: "{{param.build_command}} && {{param.test_command}}"
    evidence_refs: [test-log]
```

This is how a flow stays reusable across stacks as one contract — the stack-specific commands resolve from parameters — instead of forking into a separate per-stack flow, which the `docs/goals.md` non-goal forbids. `flowctl validate` rejects a `{{param.x}}` reference whose `x` is not declared, and requires `enum` parameters to declare a non-empty `choices` list.

## Sub-flow composition

Under `spec_version: agentic-flows/v1.1`, a `flow_ref` node runs another flow as a single step. It names a child flow and version range, binds parent values into the child's inputs, and lifts named child outputs into local artifacts:

```yaml
- id: backend
  type: flow_ref
  title: Build backend
  description: Run the backend-service sub-flow.
  ref:
    flow_id: engineering.backend-service
    version_constraint: ">=0.1.0 <0.2.0"
  with:
    target_spec: "{{artifact.design-spec}}"
    stack: "{{input.stack}}"
  expose:
    service_patch: backend-patch
  requires: [design-spec]
  produces: [backend-patch]   # must equal the expose targets
```

The child runs as its own run bundle; the parent links to it (never inlines it), so each child keeps independent versioning and evidence.

`flowctl check-composition` runs the static checks against the flow catalog:

- `ref.flow_id` resolves to a catalog flow and `version_constraint` is a satisfiable semver range.
- every `with` key is a declared child input, and every required child input is bound.
- every `expose` key is a declared child output, and `produces` equals the set of exposed artifact names.
- the parent's `required_capabilities` is a superset of the union of the children's, and `supported_cores` is a subset of their intersection.
- the cross-flow `flow_ref` graph has no cycles.

The run-time arm is folded into `flowctl validate-run` (see [Run validation](#run-validation)).

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
- for a `flow_ref` flow, every `flow_ref` node has a matching `sub_runs` entry whose child run bundle recursively validates, is `completed`, and has its own required gates passed
- each `sub_runs` entry references a real `flow_ref` node, and each `flow_ref` node has a `subflow.completed` event

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
