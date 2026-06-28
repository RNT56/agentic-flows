# Codebase orientation

Use this flow to build a quick, verified map of an unfamiliar repository before changing it: entrypoints, tests, build commands, ownership boundaries, and risks.

The core shape is:

1. Intake the repo target and the orientation focus.
2. Scan the layout, entrypoints, and ownership boundaries.
3. Probe the build and test commands by running them.
4. Synthesize the orientation map and the verified commands.
5. Verify the map identifies the key elements.
6. Close out with the map and the commands.

If those independent projects choose to consume this flow, NilCore can run the scan and probes in a sandboxed worker.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/research/codebase-orientation.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/codebase-orientation.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | NilCore has a repo-local contract smoke. |
| Promotion gate | Open | Needs one real NilCore adapter smoke result before `stable`. |
