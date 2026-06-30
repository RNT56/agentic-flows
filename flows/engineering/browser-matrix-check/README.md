# Browser matrix check

Render a built UI and run deterministic assertions across a parameterized browser and viewport matrix in a provisioned headless browser, with per-instance evidence.

The core shape is:

1. Intake matrix scope.
2. Plan the matrix.
3. Run the browser matrix (fans out over each `target`, provisions a `headless-browser`).
4. Document viewport coverage.
5. Verify matrix results.
6. Close out (after teardown).

The browser/viewport matrix is a `targets` input fanned out with `fan_out` (bounded cardinality, `all_pass`), never a per-browser flow fork. Supported consumers: nilcore.

This is the single parameterized form of browser-regression and cross-platform-regression: one node fans out over N target instances, each rendering in a runtime-provisioned headless browser, producing per-instance `sandbox-run` evidence (assertions and console output) plus deterministic coverage documentation. A failing instance fails the `all_pass` gate.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, parameters, fan-out bounds, environment, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/browser-matrix-check.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/browser-matrix-check.run.json` is a NilCore run with per-target `sandbox-run` evidence and provisioning provenance. |
| Optional consumers | Preview | NilCore run evidence only; needs a runtime that provisions a headless browser. |
| Promotion gate | Open | Needs real adapter smoke evidence before `stable`. |
