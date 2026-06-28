# Handoff and resume

Use this flow to compact current work into a handoff packet so another agent or a future run can resume cleanly, with state, decisions, blockers, validation status, and next commands preserved.

The core shape is:

1. Intake the current session state and the next owner.
2. Compact the session into a snapshot.
3. Assemble the handoff packet and an ordered resume checklist.
4. Verify completeness of the handoff.
5. Close out with the handoff packet and resume checklist.

If those independent projects choose to consume this flow, ThinClaw can persist the handoff as durable state and NilCore can resume it in a fresh worker.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/orchestration/handoff-and-resume.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/handoff-and-resume.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | NilCore has a repo-local contract smoke; ThinClaw support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
