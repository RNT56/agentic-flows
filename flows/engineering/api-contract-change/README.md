# API contract change

Change an API contract while enumerating consumers, updating docs and tests, and proving compatibility.

The core shape is:

1. Intake contract change.
2. Enumerate consumers.
3. Apply change and updates.
4. Run checks.
5. Verify compatibility.
6. Close out change.

Supported consumers: nilcore, crustcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/api-contract-change.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/api-contract-change.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `crustcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
