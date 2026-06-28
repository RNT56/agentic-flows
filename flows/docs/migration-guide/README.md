# Migration guide

Use this flow to write a migration guide for a breaking change: compare the old and new behavior, give ordered steps, and include a rollback.

The core shape is:

1. Intake the breaking change and the audience.
2. Compare the old and new behavior.
3. Write ordered migration steps and a rollback.
4. Verify behavior is compared, steps are ordered, and rollback is included.
5. Close out with the migration guide and the steps.

If those independent projects choose to consume this flow, NilCore can produce the guide in a sandboxed worker; standalone runners can publish it directly.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/docs/migration-guide.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/migration-guide.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | NilCore has a repo-local contract smoke. |
| Promotion gate | Open | Needs one real NilCore adapter smoke result before `stable`. |
