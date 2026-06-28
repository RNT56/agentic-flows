# Repository bootstrap

Initialize a new repo with docs, CI, license, and a first release plan, proving the toolchain runs.

The core shape is:

1. Intake project brief.
2. Plan the scaffold.
3. Create the scaffold.
4. Run CI locally.
5. Verify bootstrap.
6. Close out bootstrap.

Supported consumers: nilcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/repository-bootstrap.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/repository-bootstrap.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `nilcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
