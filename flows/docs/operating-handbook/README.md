# Operating handbook

Create or refresh a project operating handbook with a linked index, runnable commands, and no stale claims.

The core shape is:

1. Intake handbook scope.
2. Inventory docs.
3. Run documented commands.
4. Write the handbook.
5. Verify the handbook.
6. Close out handbook.

Supported consumers: nilcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/docs/operating-handbook.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/operating-handbook.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `nilcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
