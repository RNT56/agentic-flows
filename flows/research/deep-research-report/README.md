# Deep research report

Use this flow when the user needs an evidence-backed written answer instead of a short lookup.

The verifier step exists to compare sources before writing. It should flag stale evidence, source conflicts, and claims that are not supported strongly enough for the decision.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/research/deep-research-report.sample.json` covers required inputs and expected outputs. |
| Run evidence | Open | Needs a completed run bundle with source-log, synthesis notes, report, and bibliography evidence. |
| Optional consumers | Experimental | ThinClaw, NilCore, and standalone support are declared as optional adapter intent. |
| Promotion gate | Open | Needs source freshness, citation quality, and conflict-resolution evidence before `preview`. |
