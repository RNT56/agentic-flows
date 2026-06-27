# Core integration

This repository is a shared workflow definition layer. ThinClaw, NilCore, and CrustCore should consume it through a small adapter rather than by hard-coding per-flow behavior.

## Shared adapter contract

Every runtime adapter should:

1. Load `flow.yaml`.
2. Validate it against `schemas/flow.schema.json`.
3. Confirm that its own core is present in `runtime.supported_cores`.
4. Confirm that `runtime.required_capabilities` are available.
5. Execute or record nodes in graph order.
6. Emit events compatible with `schemas/event.schema.json`.
7. Attach evidence for required quality gates.

## ThinClaw

ThinClaw should treat flows as durable routines.

Recommended mapping:

- `intake` -> operator request and memory context.
- `plan` -> routine plan state.
- `approval` -> explicit operator decision.
- `finalizer` -> durable closeout entry.

ThinClaw should preserve decisions, rejected outputs, and final evidence so future routines can learn from prior operator choices.

## NilCore

NilCore should treat flows as supervised work plans.

Recommended mapping:

- `agent_task` -> worker job.
- `tool` -> sandboxed command or browser action.
- `verifier` -> supervisor verification step.
- `handoff` -> lane or worker transfer.

NilCore should own concurrency, sandbox boundaries, retries, and worker result collection.

## CrustCore

CrustCore should treat flows as proof contracts.

Recommended mapping:

- `quality_gates` -> verifier-owned completion criteria.
- `patch` outputs -> patch evidence.
- `approval` nodes -> audit boundary.
- `observability.events` -> proof timeline.

CrustCore should reject completion when required gates are missing or evidence cannot be tied to the claimed output.

## Compatibility rule

Do not mark a flow `stable` until each supported core has loaded it and satisfied its required capabilities without per-flow custom code.

