# Market and user value

Evaluate whether a product idea has real user value and differentiation, ending with a next experiment.

The core shape is:

1. Intake idea.
2. Analyze user and pain.
3. Compare alternatives.
4. Assess value.
5. Close out assessment.

Supported consumers: thinclaw, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/research/market-and-user-value.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/market-and-user-value.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `thinclaw` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
