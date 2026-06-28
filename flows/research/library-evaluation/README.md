# Library evaluation

Use this flow to decide whether to adopt a library or framework: inspect the primary docs, check maintenance and license, weigh integration risk, and make an adopt-or-avoid recommendation.

The core shape is:

1. Intake the library and the requirements.
2. Inspect the primary documentation for fit.
3. Check maintenance, license, and a smoke import.
4. Assess integration risk into an evaluation.
5. Recommend adopting or avoiding the library.
6. Close out with the recommendation and the evaluation.

If those independent projects choose to consume this flow, ThinClaw can present the recommendation to the operator and NilCore can run the checks in a sandboxed worker.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/research/library-evaluation.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/library-evaluation.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | ThinClaw has a repo-local contract smoke; NilCore support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
