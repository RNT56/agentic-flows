# Event and evidence bridge

Use this flow to turn a runtime's own logs into portable `agentic-flows` evidence: a validated event stream and run bundle that any consumer can inspect. It is the seam that lets independent runtimes emit standard evidence without sharing a runtime.

The core shape is:

1. Intake the runtime-native logs and the source flow.
2. Convert log entries into event-stream events and a run bundle.
3. Validate the produced stream against the source flow metadata.
4. Close out with a validated run bundle and a conversion report.

If those independent projects choose to consume this flow, NilCore can run the conversion in a sandboxed worker, CrustCore can treat the validated bundle as proof input, and ThinClaw can attach the bundle to durable routine state.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/ops/event-and-evidence-bridge.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/event-and-evidence-bridge.run.json` and a multi-file stream under `examples/streams/event-and-evidence-bridge/` include completed gate and output evidence. |
| Optional consumers | Preview | NilCore has a repo-local contract smoke; CrustCore and ThinClaw support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
