# Human-in-the-loop review

Use this flow as a reusable approval wrapper around any other workflow output.

The decision record should be durable enough for any independent consumer to retain, including possible ThinClaw memory, NilCore supervisor logs, or CrustCore audit evidence.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/general/human-in-the-loop-review.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/human-in-the-loop-review.run.json` includes approval events and decision-record evidence. |
| Optional consumers | Preview | ThinClaw, NilCore, CrustCore, and standalone support are declared as optional adapter intent. |
| Promotion gate | Open | Needs durable approval persistence evidence in at least one real consumer before `stable`. |
