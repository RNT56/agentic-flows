# Issue backlog grooming

Triage issues into priority, owner, reproduction status, and next action, citing evidence for each.

The core shape is:

1. Intake issues.
2. Triage issues.
3. Map duplicates and blockers.
4. Verify dispositions.
5. Close out grooming.

Supported consumers: thinclaw, nilcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/issue-backlog-grooming.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/issue-backlog-grooming.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `thinclaw` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
