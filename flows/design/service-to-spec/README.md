# Service design to spec

Turn a service or API brief into an approved, traceable backend spec: endpoints, data model, auth surface, and acceptance criteria.

The core shape is:

1. Intake brief.
2. Outline endpoints.
3. Design the data model and auth surface.
4. Write traceable acceptance criteria.
5. Assemble the service spec.
6. Service architect sign-off.
7. Close out design.

This is the Design-phase sibling of `design.website-to-spec` for backend services: its `design_spec` output is shaped as the `engineering.backend-service` `target_spec` input, so the two compose directly. The `spec-approved` gate is a `judgment` gate — the architect who signs off must not be one of the producing agents (no self-review). Supported consumers: thinclaw, nilcore, standalone.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/design/service-to-spec.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/service-to-spec.run.json` includes a deterministic traceability gate and a judgment sign-off with reviewer evidence. |
| Optional consumers | Preview | Standalone run evidence (deterministic + judgment); other listed consumers are adapter intent. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
