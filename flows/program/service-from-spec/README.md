# Service from spec program

Compose service design-to-spec, backend build, and integration verification into one Design-Build-Verify program for a backend service.

It composes three sub-flows via `flow_ref`:

1. Intake brief and plan.
2. `flow_ref` -> `design.service-to-spec` (exposes the design spec).
3. `flow_ref` -> `engineering.backend-service` (builds against the spec; exposes the service patch).
4. `flow_ref` -> `ops.integration-test-lab` (verifies against a provisioned stack; exposes the integration report).
5. Verify, sign off, and close out.

This spans three lifecycle quadrants (Design -> Build -> Verify), one stage further than `program.webapp-build`. Each child runs as its own run bundle; `flowctl validate-run` recursively validates each `sub_runs` child and confirms its required gates passed. Supported consumers: nilcore (the intersection of the children's cores, since the integration lab is sandbox-only).

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` plus `flowctl check-composition` cover the graph, bindings, and `flow_ref` resolution. |
| Sample contract | Ready | `examples/samples/program/service-from-spec.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/service-from-spec.run.json` recursively validates three completed child run bundles (design, backend, integration lab). |
| Optional consumers | Preview | NilCore run evidence; the integration child needs a runtime that provisions an ephemeral stack. |
| Promotion gate | Open | Needs real adapter smoke evidence and a runtime that drives the child flows before `stable`. |
