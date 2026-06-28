# Docs from diff

Use this flow to decide whether a code change needs documentation, example, or changelog updates, and to make those updates or explicitly justify why none are needed.

The core shape is:

1. Intake the diff and the documentation root.
2. Analyze whether the change touches documented behavior.
3. Decide explicitly whether docs updates are required.
4. Update the affected docs.
5. Verify the decision is explicit and updates were made or justified.
6. Close out with the docs decision and the documentation patch.

If those independent projects choose to consume this flow, NilCore can run the analysis and updates in a sandboxed worker.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/docs-from-diff.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/docs-from-diff.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | NilCore has a repo-local contract smoke. |
| Promotion gate | Open | Needs one real NilCore adapter smoke result before `stable`. |
