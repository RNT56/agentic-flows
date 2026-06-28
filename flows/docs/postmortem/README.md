# Postmortem

Use this flow to produce a blameless postmortem: a source-cited timeline, the impact, the contributing causes, the explicit unknowns, and action items that each have an owner.

The core shape is:

1. Intake the incident summary and the available sources.
2. Assemble a source-cited timeline.
3. Analyze impact, causes, and owned action items without blame.
4. Verify the timeline cites sources, action items have owners, and unknowns are explicit.
5. Close out with the postmortem and the action items.

If those independent projects choose to consume this flow, ThinClaw can track the action items as durable follow-ups; standalone runners can inspect the postmortem directly.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/docs/postmortem.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/postmortem.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | ThinClaw has a repo-local contract smoke; standalone inspection is supported directly. |
| Promotion gate | Open | Needs one real ThinClaw adapter smoke result before `stable`. |
