# Adapter implementation plan

This plan tracks how independent projects such as ThinClaw, NilCore, and CrustCore can consume `agentic-flows` while staying separate projects.

## Shared sequence

1. Vendor or pin `agentic-flows` by commit.
2. Load `flow.yaml`.
3. Validate the schema.
4. Check `runtime.supported_cores`.
5. Check `runtime.required_capabilities`.
6. Build the node graph.
7. Execute or record node state.
8. Emit valid events.
9. Attach required gate evidence.
10. Return outputs matching `contracts.outputs`.

## Repo-local smoke evidence

This repository includes adapter smoke manifests under `examples/adapters/`.

Run:

```bash
flowctl validate-adapter-smoke examples/adapters/
```

These manifests prove contract coverage in this repo. The first external adapter seams now live in the independent repositories; this repo still validates only its portable contracts and smoke evidence.

## First external adapter status

The first implementation pass is intentionally narrow:

| Project | External module | Verified behavior | Focused validation |
| --- | --- | --- | --- |
| ThinClaw | `crates/thinclaw-agent/src/agentic_flows.rs` | Builds a manual routine from a selected flow reference and records approval metadata with flow id, version, and source. | `cargo test -p thinclaw-agent agentic_flows` |
| NilCore | `internal/agenticflows/` | Maps `agent_task` nodes to spawn subtasks, reports unsupported capabilities, and executes `tool` plans only through `sandbox.Sandbox`. | `go test ./internal/agenticflows` |
| CrustCore | `crates/crustcore-flow/src/agentic_flows.rs` | Maps required gates to verifier-owned criteria and rejects patch completion when evidence refs are missing. | `cargo test -p crustcore-flow agentic_flows` |

These adapters do not make the projects dependent on one another. Each adapter is optional, local to its repo, and consumes a decoded or selected flow shape instead of embedding a new runtime in `agentic-flows`.

## ThinClaw lane

Goal: optionally load flows as durable routines.

Status: first adapter seam implemented in ThinClaw.

Tasks:

- Build routine state from a selected, validated flow reference.
- Map approval decisions to durable metadata that includes flow id, version, and source.
- Keep direct YAML loading outside the routine builder so ThinClaw can choose vendoring or pinned-source loading later.
- Test with `general.human-in-the-loop-review`-style metadata.

Acceptance gate:

- ThinClaw can create a routine from a flow and record an approval event without requiring changes in NilCore or CrustCore.

## NilCore lane

Goal: optionally use flows as supervised worker plans.

Status: first adapter seam implemented in NilCore.

Tasks:

- Consume a decoded flow subset from a pinned or vendored source.
- Dispatch `agent_task` nodes as worker jobs.
- Run `tool` nodes through a configured sandbox.
- Reject unsupported capabilities before dispatch.
- Test with `collaboration.multi-agent-supervisor`-style worker plans.

Acceptance gate:

- NilCore can dispatch a two-node worker plan and return valid events without requiring changes in ThinClaw or CrustCore.

## CrustCore lane

Goal: optionally use flows as verifier and proof contracts.

Status: first adapter seam implemented in CrustCore.

Tasks:

- Map `quality_gates` to verifier-owned criteria.
- Require evidence for required gates.
- Reject patch completion when required evidence is incomplete.
- Keep imported flow metadata advisory until CrustCore verifier evidence exists.
- Test with `coding.feature-implementation`-style gate evidence.

Acceptance gate:

- CrustCore rejects completion without required gate evidence and accepts completion when evidence is present without requiring changes in ThinClaw or NilCore.

## Cross-core compatibility

A flow can be promoted to stable for a listed optional consumer only after that independent project has adapter evidence.

Required evidence:

- loader output
- capability check result
- event validation result
- quality gate validation result
- notes for any adapter-specific mapping
