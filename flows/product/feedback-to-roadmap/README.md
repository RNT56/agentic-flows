# Feedback to roadmap

Turn collected user feedback into cited themes, opportunities, and prioritized tasks with rationale.

The core shape is:

1. Intake feedback.
2. Cluster into themes.
3. Prioritize opportunities.
4. Verify synthesis.
5. Close out roadmap.

Supported consumers: thinclaw, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/product/feedback-to-roadmap.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/feedback-to-roadmap.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `thinclaw` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
