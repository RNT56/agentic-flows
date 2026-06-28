# Dead code retirement

Use this flow to prove a piece of code is unused, remove it, and verify behavior is unchanged, or keep it with a justification when it is still referenced.

The core shape is:

1. Intake the suspected dead code and the repo target.
2. Search the codebase for references and public API exposure.
3. Decide confirmed-unused or still-referenced.
4. Remove the confirmed-unused code.
5. Run checks to confirm behavior is unchanged.
6. Verify impact and close out with the removal patch and an impact report.

If those independent projects choose to consume this flow, NilCore can run the search, removal, and checks in a sandboxed worker.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/dead-code-retirement.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/dead-code-retirement.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | NilCore has a repo-local contract smoke. |
| Promotion gate | Open | Needs one real NilCore adapter smoke result before `stable`. |
