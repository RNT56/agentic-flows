# Adapter certification

Use this flow to produce adapter smoke evidence for a consumer and a flow: a loader result, a capability check, a validated run bundle, and a negative fixture that must fail as expected. Its deliverable is the adapter smoke artifact itself.

The core shape is:

1. Intake the consumer and the flow to certify.
2. Run the loader, check capability support, and validate the run bundle.
3. Confirm the manifest validates and the negative fixture fails with the expected error.
4. Close out with the adapter smoke manifest and a certification report.

If those independent projects choose to consume this flow, CrustCore can own the certification as adapter proof, NilCore can run it as a sandboxed job, and ThinClaw can record the certification result against the source flow version.

## Runnable

This flow is **runnable** by the reference runner: its `certify` tool node runs a real command. Run it against this repo's adapter smokes:

```
flowctl run flows/ops/adapter-certification/flow.yaml \
  --input "consumer=nilcore" \
  --input "flow=file://flows/research/codebase-orientation/flow.yaml" \
  --param "smoke_manifest=examples/adapters" \
  --out examples/runs/real/adapter-certification
```

The runner executes `flowctl validate-adapter-smoke`, captures its real output as the `adapter-smoke-log` artifact, passes the `adapter-smoke-validates` gate from that evidence, and writes a validating run bundle. A produced example lives at `examples/runs/real/adapter-certification/`.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/ops/adapter-certification.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/adapter-certification.run.json` includes a completed command gate and output evidence. |
| Real run | Ready | `examples/runs/real/adapter-certification/` is produced by `flowctl run` with real `flowctl validate-adapter-smoke` output. |
| Optional consumers | Preview | CrustCore has a repo-local contract smoke; NilCore and ThinClaw support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
