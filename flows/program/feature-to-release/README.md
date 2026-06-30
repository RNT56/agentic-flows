# Feature to release program

Compose issue-to-verified-pr and ephemeral preview deploy into one Build-Ship-Govern program, gated by an independent release acceptance.

It composes two sub-flows via `flow_ref`:

1. Intake issue and plan.
2. `flow_ref` -> `engineering.issue-to-verified-pr` (exposes the verified patch).
3. `flow_ref` -> `ops.ephemeral-preview-deploy` (deploys to a preview; exposes the deploy record).
4. Verify, accept, and close out.

This closes the Build -> Ship -> Govern loop and is the honest substitute for an end-to-end release autopilot: it stops at a preview deploy and an independent `acceptance` gate (reviewer-identity), never a fabricated production rollout or an irreversible tag/publish. The verified-patch acceptance is modeled as an in-program acceptance gate rather than a `flow_ref`, because `proof.verified-patch-acceptance` and `ops.ephemeral-preview-deploy` share no supported core. Supported consumers: nilcore.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` plus `flowctl check-composition` cover the graph, bindings, and `flow_ref` resolution. |
| Sample contract | Ready | `examples/samples/program/feature-to-release.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/feature-to-release.run.json` recursively validates two completed child run bundles (build, preview deploy). |
| Optional consumers | Preview | NilCore run evidence; the preview-deploy child needs a runtime that provisions a preview target. |
| Promotion gate | Open | Needs real adapter smoke evidence and a runtime that drives the child flows before `stable`. |
