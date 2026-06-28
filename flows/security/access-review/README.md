# Access review

Review user, connector, repo, and deployment permissions so each has an owner and reason, tracking removals.

The core shape is:

1. Intake access.
2. Normalize inventory.
3. Review grants.
4. Verify review.
5. Close out review.

Supported consumers: thinclaw, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/security/access-review.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/access-review.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `thinclaw` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
