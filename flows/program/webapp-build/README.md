# Web app build program

Compose the design-to-spec, backend, and frontend sub-flows into one evidence-backed web application build program.

This is the first flow to use `flow_ref` sub-flow composition (`agentic-flows/v1.1`). It runs three child flows as steps:

1. Intake brief.
2. Plan the build program.
3. `flow_ref` -> `design.website-to-spec` (exposes the design spec).
4. `flow_ref` -> `engineering.backend-service` (exposes the backend patch).
5. `flow_ref` -> `engineering.frontend-build` (exposes the frontend patch).
6. Integrate and verify.
7. Operator sign-off.
8. Close out program.

Each child runs as its own run bundle with its own gates and evidence; the program links to them via `sub_runs`. Supported consumers: nilcore, standalone (the intersection of the children's supported cores).

## Composition evidence

The `subflows-passed` gate is not a self-assertion. `flowctl validate-run` recursively validates each `sub_runs` child bundle and requires it to be `completed` with its own required gates passed; `flowctl check-composition` statically checks the `flow_ref` resolution, bindings, capabilities, and the absence of cycles. A parent that claims completion without honest child evidence is rejected.

- Static: `flowctl check-composition flows/program/webapp-build/flow.yaml`
- Runtime: `flowctl validate-run examples/runs/webapp-build.run.json` (recursively validates `examples/runs/webapp/{design,backend,frontend}.run.json`)

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` plus `flowctl check-composition` cover the graph, bindings, and `flow_ref` resolution. |
| Sample contract | Ready | `examples/samples/program/webapp-build.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/webapp-build.run.json` recursively validates three completed child run bundles. |
| Optional consumers | Preview | Standalone run evidence only; other listed consumers are adapter intent. |
| Promotion gate | Open | Needs real adapter smoke evidence and a runtime that provides `subflow.dispatch` before `stable`. |
