# CLI tool build

Build a scoped command-line tool in a given stack with build, test, and golden-output evidence and a documented command surface.

The core shape is:

1. Intake tool scope.
2. Plan the tool.
3. Implement the tool (iterates until build and tests pass, bounded).
4. Build and test.
5. Check golden output.
6. Document the command surface.
7. Verify and close out.

The stack is a contract input and the build/test/golden commands are parameters, so one flow covers many stacks. The implement node uses a bounded `iteration` loop (`max_iterations: 3`, `until: gate:build-and-tests-pass`). Every gate is deterministic, so a standalone run bundle is genuine proof. Supported consumers: nilcore, standalone.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/cli-tool.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/cli-tool.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | Standalone run evidence (fully deterministic); other listed consumers are adapter intent. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
