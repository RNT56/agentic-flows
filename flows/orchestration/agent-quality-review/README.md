# Agent quality review

Use this flow to review an agent's work for hallucinated claims, missed validation, and unsafe edits, producing cited findings and an explicit statement of residual risk.

The core shape is:

1. Intake the agent output, its claims, and the evidence it cited.
2. Check each claim against its evidence and flag unsafe edits.
3. Assess findings for citations, drop false positives, and state residual risk.
4. Close out with the review report and the cited findings.

If those independent projects choose to consume this flow, CrustCore can own the review as quality proof; standalone runners can inspect the findings directly.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/orchestration/agent-quality-review.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/agent-quality-review.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | CrustCore has a repo-local contract smoke; standalone inspection is supported directly. |
| Promotion gate | Open | Needs one real CrustCore adapter smoke result before `stable`. |
