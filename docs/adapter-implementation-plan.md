# Adapter implementation plan

This plan tracks how independent projects such as ThinClaw, NilCore, and CrustCore could choose to consume `agentic-flows`.

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

## ThinClaw lane

Goal: optionally load flows as durable routines.

Tasks:

- Add a loader for validated flow documents.
- Map `intake`, `plan`, `approval`, and `finalizer` nodes to routine state.
- Persist operator decisions with `flow_id`, `flow_version`, `run_id`, and node id.
- Add a smoke test using `general.human-in-the-loop-review`.

Acceptance gate:

- ThinClaw can create a routine from a flow and record an approval event without requiring changes in NilCore or CrustCore.

## NilCore lane

Goal: optionally use flows as supervised worker plans.

Tasks:

- Add a loader for validated flow documents.
- Dispatch `agent_task` nodes as worker jobs.
- Run `tool` nodes in a configured sandbox.
- Route `verifier` nodes through supervisor checks.
- Add a smoke test using `collaboration.multi-agent-supervisor`.

Acceptance gate:

- NilCore can dispatch a two-node worker plan and return valid events without requiring changes in ThinClaw or CrustCore.

## CrustCore lane

Goal: optionally use flows as verifier and proof contracts.

Tasks:

- Add a loader for validated flow documents.
- Map `quality_gates` to verifier-owned criteria.
- Require evidence for required gates.
- Tie patch outputs to proof artifacts.
- Add a smoke test using `coding.feature-implementation`.

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
