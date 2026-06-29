# Runnable, consumable flows

This document defines what makes a flow **consumable** (a runtime can run it without re-inventing the workflow) and **runnable** (the bundled reference runner can execute it locally and emit real evidence). It is the authoring standard for the substance layer added in `agentic-flows/v1`.

## The substance layer

Beyond the graph (`nodes`, `edges`, `quality_gates`), each node may carry the content a consumer needs to actually execute the step. All fields are optional and additive, so existing flows keep validating, but a flow is only **consumable** once its working nodes carry them.

| Field | On node types | Purpose |
| --- | --- | --- |
| `instructions` | `agent_task`, `verifier`, `plan`, `decision`, `approval`, `finalizer`, `intake` | The actual guidance: the prompt for an agent step, the criteria for a verifier, the question for an approval. This is the portable know-how. |
| `command` | `tool`, and optionally `verifier`/`agent_task` | The concrete command to run. Supports `${param.NAME}` and `${input.NAME}` substitution. This is what makes a node executable by the reference runner. |
| `inputs_schema` | any | Structured inputs the node consumes, by `id`/`type`, so a runtime can wire steps mechanically. |
| `outputs_schema` | any | Structured outputs the node produces. |
| `parameters` | any | Typed, defaulted knobs a consumer can set without editing the flow. |
| `on_failure` | any | Declared `retry` / `abort` / `escalate` / `skip` behavior, with `max_attempts` and an optional `fallback_node`. |

Runtime-specific bindings stay out of the portable flow: which agent model, the sandbox, secrets, credentials, the concrete tool runtime, and the approval surface belong to the consumer and to `runtime.adapter_hints`.

## What stays in the consumer

A portable flow says *what* to do and *how to check it*. The consumer supplies *the means*:

- the agent that satisfies an `agent_task` (the flow gives the `instructions`; the runtime gives the model and tools);
- the sandbox and permissions a `command` runs under;
- secrets and credentials;
- the approval channel for an `approval` node.

This is the line that keeps a flow portable across ThinClaw, NilCore, CrustCore, and the reference runner.

## The reference runner: `flowctl run`

`flowctl run <flow.yaml> [--input id=value ...] [--param id=value ...] [--workdir DIR] [--out DIR]` executes a flow with **local handlers only** and writes a real run bundle plus real artifact files.

Execution model:

1. Nodes run in dependency order (a topological order over `requires`/`produces` from the entrypoint).
2. Each node is dispatched to a handler by type:
   - **`tool`** (or any node with a `command`): the command is run as a subprocess in `--workdir`; stdout, stderr, and exit code are captured to a real log artifact. A non-zero exit triggers `on_failure`.
   - **`intake`**: records the provided inputs as a JSON artifact.
   - **`plan` / `decision` / `verifier` / `finalizer`**: an *assemble* handler renders `instructions` and writes the node's declared `produces` to artifacts; `verifier` additionally checks that required-gate evidence artifacts exist.
   - **`agent_task` / `approval` / `handoff`** without a `command`: require a consumer-provided handler. In standalone mode with no handler, the node is recorded as `needs-handler` and the run completes with status `incomplete` — the runner never pretends an agent ran.
3. After execution, each required quality gate is marked `passed` only if its `evidence_refs` artifacts were actually produced on disk.
4. A run bundle is written to `--out` with `file://` artifact URIs pointing at files that exist, real timestamps, and a `gate.completed` event per passed gate. The bundle validates against `schemas/run.schema.json`.

## Binding consumer handlers

A consuming runtime supplies the handlers a contract flow leaves open, instead of baking commands into the flow. `flowctl run` models this with `--handler node_id=command`: it binds an `agent_task`, `approval`, or `handoff` node to a command at run time. The bound command runs exactly like a node `command` (same `${param.*}`/`${input.*}` substitution, same `on_failure` policy, same artifact capture), and its `node.completed` event is tagged `handler: consumer` so the bundle records that the step was satisfied by a consumer binding rather than the flow itself.

```
flowctl run flows/coding/feature-implementation/flow.yaml \
  --input "task=..." --input "repo=." \
  --param "test_command=python -m pytest -q" \
  --handler "implement=<the consumer's coding-agent command>" \
  --handler "approval=<the consumer's approval command>"
```

This is how the catalog's contract flows are consumed end-to-end. The flow stays runtime-neutral; the runtime owns the binding. A worked example with a committed bundle lives under [`examples/runs/consumed/`](../examples/runs/consumed/README.md). Handlers that target an unknown node id are rejected before the run starts.

To see a flow's consumption surface before running it, use `flowctl run <flow> --plan`. It prints the execution order and classifies each node as `command` (the flow runs it), `data` (the runner assembles it), `handler` (a supplied `--handler` binds it), or `needs-handler` (a consumer must bind it), then lists exactly which nodes to bind. Pass the same `--handler` flags with `--plan` to confirm a binding set is complete before executing — when nothing remains, it reports `nothing (runnable as-is)`. Every catalog flow has a well-defined surface: a node is always a data step, a command step, or a clearly-named node a consumer binds.

To check a flow's wiring without running anything, use `flowctl run <flow> --simulate`. It assumes every working and agent step succeeds and produces its declared outputs, then verifies that each required quality gate is satisfiable from produced evidence and that every required output is produced — surfacing a gate that references an artifact no node emits, or a required output nothing produces. A test runs `--simulate` over the whole catalog and asserts every flow reaches `status: completed`, so the library carries a structural completability guarantee: with its working steps satisfied, every flow runs to a complete, gated result.

A flow is **runnable** when `flowctl run` can take it to `status: completed` with local handlers alone (i.e., its working nodes are `tool`/`command` or data steps). A flow is a **contract** when it needs a consumer to supply an `agent_task`/`approval` handler; it is still fully consumable — bind the handlers and it runs to completion, the runtime providing the agent and the flow providing everything else.

## Runnable flows today

These flows reach `status: completed` under `flowctl run` with no consumer handler, and ship a real produced run bundle under `examples/runs/real/`:

| Flow | What runs | Real evidence |
| --- | --- | --- |
| [`research.codebase-orientation`](../flows/research/codebase-orientation/README.md) | `git ls-files` + the project test command | real repo scan and `pytest` output |
| [`ops.adapter-certification`](../flows/ops/adapter-certification/README.md) | `flowctl validate-adapter-smoke` | real adapter-smoke validation output |
| [`proof.verified-patch-acceptance`](../flows/proof/verified-patch-acceptance/README.md) | the verifier-owned check command (`python -m pytest -q`) | real test output backing the verdict |
| [`ops.capability-negotiation`](../flows/ops/capability-negotiation/README.md) | no commands - a fail-closed capability comparison | assembled decision record |

Every other catalog flow is a consumable contract: it carries full instructions, typed I/O, parameters, and concrete commands on its tool steps, but its creative core is an `agent_task` that a consuming runtime supplies the agent for. The reference runner reports those nodes as `needs-handler` rather than faking them.

## Authoring checklist

A flow is ready to call consumable when:

1. Every `agent_task`/`verifier`/`approval` node has `instructions`.
2. Every `tool` node has a `command` (or an explicit note that the consumer binds it).
3. Each node declares `inputs_schema`/`outputs_schema` for anything it consumes or produces.
4. Tunable values are `parameters` with types and defaults, not hard-coded.
5. At least one required quality gate has `evidence_refs` backed by a real produced artifact.
6. `on_failure` is set wherever a step can fail in a way that should not silently pass.
7. Runnable flows ship a real run bundle produced by `flowctl run`; contract flows document the handler a consumer must supply.
