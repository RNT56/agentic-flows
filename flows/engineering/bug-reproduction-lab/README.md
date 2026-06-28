# Bug reproduction lab

Use this flow to turn a bug report into a minimal reproduction and a test that fails before any fix, or an explicit explanation of why it cannot be reproduced.

The core shape is:

1. Intake the bug report and the repo target.
2. Attempt to reproduce the bug locally.
3. Decide reproducible or not, and record the reproduction or an impossibility note.
4. Author the smallest failing test.
5. Confirm the test fails before any fix.
6. Close out with the reproduction and the failing test.

If those independent projects choose to consume this flow, NilCore can run reproduction and test authoring in a sandboxed worker.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/bug-reproduction-lab.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/bug-reproduction-lab.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | NilCore has a repo-local contract smoke. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
