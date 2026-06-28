# Performance regression

Measure, isolate, and fix a performance regression with a recorded method and before/after numbers.

The core shape is:

1. Intake regression.
2. Measure baseline.
3. Isolate and fix.
4. Measure after.
5. Verify improvement.
6. Close out regression.

Supported consumers: nilcore, crustcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/performance-regression.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/performance-regression.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `crustcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
