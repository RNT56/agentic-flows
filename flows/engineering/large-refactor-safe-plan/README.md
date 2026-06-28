# Large refactor safe plan

Split a large refactor into reversible slices with acceptance criteria and contract tests locked first.

The core shape is:

1. Intake refactor goal.
2. Lock baseline.
3. Test shared contracts.
4. Plan reversible slices.
5. Verify the plan.
6. Close out plan.

Supported consumers: nilcore, crustcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/large-refactor-safe-plan.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/large-refactor-safe-plan.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `nilcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
