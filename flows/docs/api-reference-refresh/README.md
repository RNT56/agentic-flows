# API reference refresh

Update API docs from current schemas and types, reconciling generated and hand-written docs and validating examples.

The core shape is:

1. Intake refresh scope.
2. Generate reference.
3. Validate examples.
4. Reconcile docs.
5. Verify reconciliation.
6. Close out refresh.

Supported consumers: nilcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/docs/api-reference-refresh.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/api-reference-refresh.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `nilcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
