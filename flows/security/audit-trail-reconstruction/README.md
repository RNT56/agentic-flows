# Audit trail reconstruction

Reconstruct what happened in a run from logs, events, approvals, and artifacts, marking gaps explicitly.

The core shape is:

1. Intake sources.
2. Index sources.
3. Reconstruct timeline.
4. Verify and mark gaps.
5. Close out reconstruction.

Supported consumers: thinclaw, crustcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/security/audit-trail-reconstruction.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/audit-trail-reconstruction.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `crustcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
