# Core integration

This repository is a shared workflow definition layer for independent projects. ThinClaw, NilCore, and CrustCore may consume it later through small adapters, vendored schemas, or copied templates. No adapter is assumed to exist yet.

## Shared adapter contract

Every optional adapter should:

1. Load `flow.yaml`.
2. Validate it against `schemas/flow.schema.json`.
3. Confirm that its own project is present in `runtime.supported_cores`.
4. Confirm that `runtime.required_capabilities` are available.
5. Execute or record nodes in graph order.
6. Emit events compatible with `schemas/event.schema.json`.
7. Attach evidence for required quality gates.

## ThinClaw

ThinClaw can treat flows as durable routines if it chooses to consume this repo.

Recommended mapping:

- `intake` -> operator request and memory context.
- `plan` -> routine plan state.
- `approval` -> explicit operator decision.
- `finalizer` -> durable closeout entry.

If implemented, ThinClaw should preserve decisions, rejected outputs, and final evidence so future routines can learn from prior operator choices.

## NilCore

NilCore can treat flows as supervised work plans if it chooses to consume this repo.

Recommended mapping:

- `agent_task` -> worker job.
- `tool` -> sandboxed command or browser action.
- `verifier` -> supervisor verification step.
- `handoff` -> lane or worker transfer.

If implemented, NilCore can own concurrency, sandbox boundaries, retries, and worker result collection.

## CrustCore

CrustCore can treat flows as proof contracts if it chooses to consume this repo.

Recommended mapping:

- `quality_gates` -> verifier-owned completion criteria.
- `patch` outputs -> patch evidence.
- `approval` nodes -> audit boundary.
- `observability.events` -> proof timeline.

If implemented, CrustCore should reject completion when required gates are missing or evidence cannot be tied to the claimed output.

## Compatibility rule

Do not mark a flow `stable` for an optional consumer until that independent project has loaded it and satisfied its required capabilities without per-flow custom code.
