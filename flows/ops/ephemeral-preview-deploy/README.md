# Ephemeral preview deploy

Deploy a built artifact to a throwaway preview environment, probe its health, and capture a rollback plan, tearing the preview down afterward.

The core shape is:

1. Intake deploy scope.
2. Plan the preview deploy.
3. Run preflight checks.
4. Deploy to an ephemeral preview (provisions a `preview-deploy-target`).
5. Probe preview health.
6. Capture rollback plan.
7. Close out (after teardown).

The deploy target is a parameter (`preflight_command`, `deploy_command`, `health_check_command`, `rollback_command`), not a per-platform fork. Supported consumers: nilcore.

This is the honest form of "deploy and verify": health is probed against a runtime-provisioned **ephemeral preview**, never production. The `preview-health-probed` gate is the catalog's first `probe` gate, and its `sandbox-run` evidence is backed by a non-self-issued `env.provisioned` event with a matching `env.torn_down` — a standalone run cannot emit it. No production tag or publish happens in-flow.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, parameters, environment, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/ops/ephemeral-preview-deploy.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/ephemeral-preview-deploy.run.json` is a NilCore run with `sandbox-run` health evidence and provisioning provenance. |
| Optional consumers | Preview | NilCore run evidence only; needs a runtime that provisions preview targets. |
| Promotion gate | Open | Needs real adapter smoke evidence before `stable`. |
