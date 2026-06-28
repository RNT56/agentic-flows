# Knowledge base maintenance

Keep docs, decisions, and examples current by detecting stale items and applying sourced, conservative updates.

The core shape is:

1. Intake scope.
2. Scan for staleness.
3. Plan updates.
4. Apply updates.
5. Verify maintenance.
6. Close out maintenance.

Supported consumers: thinclaw, nilcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/program/knowledge-base-maintenance.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/knowledge-base-maintenance.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `nilcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
