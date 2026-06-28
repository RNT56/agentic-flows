# Decision record

Use this flow to capture an architectural or product decision as a durable record: the decision, the alternatives considered, the consequences, and an explicit owner and date.

The core shape is:

1. Intake the decision context and the owner.
2. Analyze the options and the rejected alternatives.
3. Write the decision record with consequences, owner, and date.
4. Verify owner and date are present and alternatives are documented.
5. Close out with the decision record and its metadata.

If those independent projects choose to consume this flow, ThinClaw can store the record as durable decision state; standalone runners can inspect it directly.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/docs/decision-record.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/decision-record.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | ThinClaw has a repo-local contract smoke; standalone inspection is supported directly. |
| Promotion gate | Open | Needs one real ThinClaw adapter smoke result before `stable`. |
