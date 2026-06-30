# Integration test lab

Run a service's integration suite against a runtime-provisioned ephemeral stack and record sandbox-run evidence with provisioning provenance.

The core shape is:

1. Intake lab scope.
2. Plan the test lab.
3. Provision the ephemeral stack (`ephemeral-datastore`, `dev-server`).
4. Run the integration suite.
5. Verify suite results.
6. Close out (after teardown).

The suite command and datastore are parameters, so one flow covers many stacks. Supported consumers: nilcore.

This gives the "needs a live DB and dependent services" tests an honest home: the suite runs against a real (ephemeral) stack the runtime stood up, so the `integration-suite-passed` gate is honest `sandbox-run` evidence backed by `env.provisioned`/`env.torn_down`, not a fabricated pass. It is the integration-verification child the release programs compose.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, parameters, environment, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/ops/integration-test-lab.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/integration-test-lab.run.json` is a NilCore run with `sandbox-run` suite evidence and provisioning provenance. |
| Optional consumers | Preview | NilCore run evidence only; needs a runtime that provisions an ephemeral stack. |
| Promotion gate | Open | Needs real adapter smoke evidence before `stable`. |
