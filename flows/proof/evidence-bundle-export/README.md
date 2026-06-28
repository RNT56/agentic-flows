# Evidence bundle export

Use this flow to export a compact, self-contained proof bundle for a completed run: the source flow version, the event stream, the gate evidence, the artifact references, and the verifier outcome.

The core shape is:

1. Intake the completed run bundle and the verifier outcome.
2. Collect the flow version, events, gate evidence, and artifact refs.
3. Assemble the compact proof bundle.
4. Verify the bundle includes every required element.
5. Close out with the proof bundle and an export manifest.

If those independent projects choose to consume this flow, CrustCore can own the exported bundle as portable proof; standalone runners can archive it directly.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/proof/evidence-bundle-export.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/evidence-bundle-export.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | CrustCore has a repo-local contract smoke; standalone inspection is supported directly. |
| Promotion gate | Open | Needs one real CrustCore adapter smoke result before `stable`. |
