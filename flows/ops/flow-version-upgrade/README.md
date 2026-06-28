# Flow version upgrade

Safely migrate a pinned consumer from one flow version to another with migration steps and a matrix update.

The core shape is:

1. Intake upgrade scope.
2. Compare versions.
3. Plan migration.
4. Update compatibility matrix.
5. Verify migration.
6. Close out upgrade.

Supported consumers: thinclaw, nilcore, crustcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/ops/flow-version-upgrade.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/flow-version-upgrade.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `thinclaw` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
