# Multi-agent supervisor

Use this flow for larger work that benefits from parallel lanes. The critical contract is lane ownership: every worker needs a bounded scope, acceptance gates, and evidence before consolidation.

If consumed by independent projects, ThinClaw is a plausible home for operator-facing supervisor state and NilCore is a plausible worker-dispatch engine. This flow does not require those projects to be integrated.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/collaboration/multi-agent-supervisor.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/multi-agent-supervisor.run.json` includes lane, worker, and merge evidence. |
| Optional consumers | Experimental | ThinClaw and NilCore support are declared as optional adapter intent only. |
| Promotion gate | Open | Needs a real worker-dispatch smoke test and conflict-reconciliation evidence before `preview`. |
