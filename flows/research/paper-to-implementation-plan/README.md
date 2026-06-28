# Paper to implementation plan

Translate a paper or spec into implementable slices and validation tasks, separating assumptions from claims.

The core shape is:

1. Intake paper.
2. Extract claims.
3. Plan slices.
4. Define validation.
5. Verify the plan.
6. Close out plan.

Supported consumers: nilcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/research/paper-to-implementation-plan.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/paper-to-implementation-plan.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `nilcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
