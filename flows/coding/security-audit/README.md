# Security audit

Use this flow for evidence-backed security review. It separates attack-surface enumeration from scanner output so the result is not just a dependency report.

High-risk findings should route through a human approval node before final output.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/coding/security-audit.sample.json` covers required inputs and expected outputs. |
| Run evidence | Open | Needs a completed audit run with scanner output, finding evidence, and severity review. |
| Optional consumers | Experimental | ThinClaw, NilCore, CrustCore, and standalone support are declared as optional adapter intent. |
| Promotion gate | Open | Needs a repeatable scanner mapping and disclosure-safe review evidence before `preview`. |
