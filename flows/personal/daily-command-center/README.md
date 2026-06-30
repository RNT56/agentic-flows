# Daily command center

Gather inboxes, calendar, routines, and pending approvals into one verified daily operating plan, with no external action without approval.

The core shape is intake -> plan -> gather -> analyze -> produce -> review -> close out. Its source gate is `external-production` — a standalone run cannot satisfy it; it is honest only on a runtime wired to the real system.

This flow is **contract-first**: the `flow.yaml`, README, and sample are authored and validate today, but no completed run bundle ships, because a completed standalone run would fabricate a runtime wired to the live inboxes, calendar, and approval surface. Supported consumers: thinclaw. The decision gate is a `judgment` gate whose reviewer must not be a producing agent.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/personal/daily-command-center.sample.json` covers required inputs and expected outputs. |
| Run evidence | Open | A completed run needs a runtime wired to the live inboxes, calendar, and approval surface; a standalone run would fabricate that state, so none ships. |
| Optional consumers | Target | Designed for thinclaw; not yet proven by an adapter. |
| Promotion gate | Open | Needs a real adapter and run from a runtime wired to the external state before `preview`/`stable`. |
