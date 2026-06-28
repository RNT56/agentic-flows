# Flow intake and routing

Use this flow when an ambiguous request must be turned into a concrete execution plan: which workflow to run, on which core, and what is still missing before work can start.

The core shape is:

1. Intake the request, target core, and obvious gaps.
2. Assemble and rank routing options against the flow catalog.
3. Select a route, or fall back to asking for more context.
4. Capture an explicit operator approval for high-risk or irreversible routes.
5. Close out with a routing decision and any outstanding questions.

If those independent projects choose to consume this flow, ThinClaw can map intake and approval to operator-facing routine state, NilCore can map the selected route to a dispatch plan, and standalone runners can inspect the routing decision directly.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/ops/flow-intake-and-routing.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/flow-intake-and-routing.run.json` includes a completed gate and output evidence. |
| Optional consumers | Preview | ThinClaw has a repo-local contract smoke; NilCore support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
