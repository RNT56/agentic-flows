# PR review and risk notes

Use this flow to review a diff for bugs, regressions, and missing tests, and to produce cited findings with a release-risk summary. It is read-only: it surfaces risk, it does not change code.

The core shape is:

1. Intake the diff and the PR intent.
2. Review the diff for bugs, regressions, and missing tests.
3. Assess findings for cited locations and severity, drop padding, and summarize risk.
4. Close out with cited findings and release-risk notes.

If those independent projects choose to consume this flow, CrustCore can treat the findings as review proof and NilCore can run the review in a sandboxed worker.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/pr-review-and-risk-notes.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/pr-review-and-risk-notes.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | CrustCore has a repo-local contract smoke; NilCore support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
