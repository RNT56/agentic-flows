# Capability negotiation

Use this flow before executing any other flow to confirm the runtime can actually satisfy what the flow requires. It compares declared required capabilities against a runtime profile and fails closed on anything missing.

The core shape is:

1. Intake the flow's required capabilities and the runtime profile.
2. Compare required against supported and build a capability matrix.
3. Decide to proceed only when everything is supported, otherwise fail closed.
4. Close out with a negotiation report and a per-capability decision.

If those independent projects choose to consume this flow, CrustCore can map the comparison to a verifier-owned policy gate, NilCore can run it as an execution preflight, and ThinClaw can surface unsupported capabilities to the operator before a routine starts.

## Runnable

This flow is **runnable** end-to-end by the reference runner. It has no command nodes - the runner assembles the comparison, the fail-closed decision, and the report from the structured intake, so it completes without a consumer-supplied handler:

```
flowctl run flows/ops/capability-negotiation/flow.yaml \
  --input 'flow_requirements={"required_capabilities":["repo.checkout","command.run","evidence.capture"]}' \
  --input 'runtime_profile={"core":"nilcore","capabilities":["repo.checkout","command.run","evidence.capture"]}' \
  --out examples/runs/real/capability-negotiation
```

It passes the `capabilities-fail-closed` gate and writes a validating run bundle. A produced example lives at `examples/runs/real/capability-negotiation/`. The evidence here is the assembled decision record rather than command output, since the flow itself runs no commands.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/ops/capability-negotiation.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/capability-negotiation.run.json` includes a completed command gate and output evidence. |
| Real run | Ready | `examples/runs/real/capability-negotiation/` is produced by `flowctl run` and completes with no consumer handler. |
| Optional consumers | Preview | CrustCore has a repo-local contract smoke; NilCore and ThinClaw support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
