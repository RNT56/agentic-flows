# Routine authoring

Turn repeated behavior into a proposed routine with trigger, action, guardrails, rollback, and approval.

The core shape is:

1. Intake behavior.
2. Draft the routine.
3. Verify the routine.
4. Approve enablement.
5. Close out routine.

Supported consumers: thinclaw, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/personal/routine-authoring.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/routine-authoring.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `thinclaw` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
