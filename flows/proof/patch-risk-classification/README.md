# Patch risk classification

Use this flow to classify a patch by reversibility, policy risk, required approval, and expected verification, failing closed on unknown risk and routing destructive changes through approval.

The core shape is:

1. Intake the patch and the policy.
2. Analyze reversibility, blast radius, and policy-relevant operations.
3. Classify the risk; unknown risk fails closed, destructive paths require approval.
4. Capture approval for destructive or unknown-risk patches.
5. Close out with the risk classification and the logged policy decision.

If those independent projects choose to consume this flow, CrustCore can own the risk policy and NilCore can run it as an execution preflight.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/proof/patch-risk-classification.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/patch-risk-classification.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | CrustCore has a repo-local contract smoke; NilCore support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
