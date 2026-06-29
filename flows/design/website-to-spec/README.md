# Website design to spec

Turn a product brief into an approved, traceable website design spec: information architecture, component inventory, and acceptance criteria.

The core shape is:

1. Intake brief.
2. Plan information architecture.
3. Build component inventory.
4. Write traceable acceptance criteria.
5. Assemble the design spec.
6. Design owner sign-off.
7. Close out design.

Supported consumers: thinclaw, nilcore, standalone. The deliverable is a concrete, checkable spec artifact, not a subjective "looks good" verdict. Independent projects map the nodes onto their own execution and approval surfaces; nothing here assumes a shared runtime.

This flow is a Design-phase producer: its `design_spec` output feeds the build flows (`engineering.backend-service`, `engineering.frontend-build`) and the `program.webapp-build` program.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/design/website-to-spec.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/webapp/design.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | Standalone run evidence only; other listed consumers are adapter intent. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
