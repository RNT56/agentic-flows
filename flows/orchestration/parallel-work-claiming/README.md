# Parallel work claiming

Use this flow to divide a broad objective into ownable lanes and register claims so that multiple agents can work in parallel without colliding on the same paths.

The core shape is:

1. Intake the objective and the currently active claims.
2. Decompose into lanes with explicit path boundaries and dependencies.
3. Register claims only for non-overlapping lanes.
4. Detect any remaining collisions.
5. Close out with lane assignments and the updated claim ledger.

If those independent projects choose to consume this flow, ThinClaw can host the shared claim board as durable state and NilCore can turn the assignments into a dispatch plan.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/orchestration/parallel-work-claiming.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/parallel-work-claiming.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | ThinClaw has a repo-local contract smoke; NilCore support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
