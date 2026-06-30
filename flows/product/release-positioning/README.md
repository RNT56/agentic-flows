# Release positioning

Produce release framing, public copy, and risk-aware rollout notes, with claims supported by shipped behavior.

The core shape is intake -> plan -> gather -> analyze -> produce -> review -> close out. Its gates are deterministic and judgment, so the contract is fully expressed; run evidence still needs a reviewer.

This flow is **contract-first**: the `flow.yaml`, README, and sample are authored and validate today, but no completed run bundle ships, because a completed standalone run would fabricate a reviewer to confirm claims against shipped behavior. Supported consumers: thinclaw, standalone. The decision gate is a `judgment` gate whose reviewer must not be a producing agent.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/product/release-positioning.sample.json` covers required inputs and expected outputs. |
| Run evidence | Open | A completed run needs a reviewer to confirm claims against shipped behavior; a standalone run would fabricate that state, so none ships. |
| Optional consumers | Target | Designed for thinclaw, standalone; not yet proven by an adapter. |
| Promotion gate | Open | Needs a real adapter and run from a runtime wired to the external state before `preview`/`stable`. |
