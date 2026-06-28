# Schema evolution

Use this flow to evolve a JSON Schema, database schema, or protocol contract safely: define a migration path, apply the change, and add fixtures that cover the new failure modes.

The core shape is:

1. Intake the proposed schema change and the repo target.
2. Plan the migration path, affected consumers, and new failure modes.
3. Apply the change and add valid and invalid fixtures.
4. Run the validators against the fixtures.
5. Verify the migration path exists and fixtures cover the new failures.
6. Close out with the migration notes and the schema patch.

If those independent projects choose to consume this flow, NilCore can run the change in a sandboxed worker and CrustCore can map the fixture checks to verifier-backed proof.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/schema-evolution.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/schema-evolution.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | NilCore has a repo-local contract smoke; CrustCore support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
