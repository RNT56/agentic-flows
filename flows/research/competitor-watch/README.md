# Competitor watch

Monitor a competitor or comparable project for product, release, and positioning changes, separating dated changes from interpretation.

The core shape is intake -> plan -> gather -> analyze -> produce -> review -> close out. Its source gate is `external-production` — a standalone run cannot satisfy it; it is honest only on a runtime wired to the real system.

This flow is **contract-first**: the `flow.yaml`, README, and sample are authored and validate today, but no completed run bundle ships, because a completed standalone run would fabricate a runtime that can retrieve the live competitor sources. Supported consumers: thinclaw, nilcore. The decision gate is a `judgment` gate whose reviewer must not be a producing agent.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/research/competitor-watch.sample.json` covers required inputs and expected outputs. |
| Run evidence | Open | A completed run needs a runtime that can retrieve the live competitor sources; a standalone run would fabricate that state, so none ships. |
| Optional consumers | Target | Designed for thinclaw, nilcore; not yet proven by an adapter. |
| Promotion gate | Open | Needs a real adapter and run from a runtime wired to the external state before `preview`/`stable`. |
