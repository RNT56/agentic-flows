# Connector grant review

Use this flow to review a connector's requested permissions before enabling it: decide the least-privilege scope per permission and require an explicit operator approval for any destructive grant.

The core shape is:

1. Intake the connector, its requested permissions, and the policy.
2. Analyze permissions against least privilege and flag destructive operations.
3. Decide the least-privilege scope.
4. Require approval before granting any destructive operation.
5. Close out with the grant decision and review notes.

If those independent projects choose to consume this flow, ThinClaw can host the approval and grant decision as durable state, and CrustCore can treat the decision as policy proof.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/security/connector-grant-review.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/connector-grant-review.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | ThinClaw has a repo-local contract smoke; CrustCore support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
