# Monorepo slice execution

Claim and execute a non-overlapping slice in a large repo with active parallel agents, reporting conflicts.

The core shape is:

1. Intake slice.
2. Claim the slice.
3. Execute the slice.
4. Run checks.
5. Verify scope and conflicts.
6. Close out slice.

Supported consumers: nilcore, thinclaw, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/monorepo-slice-execution.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/monorepo-slice-execution.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `nilcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
