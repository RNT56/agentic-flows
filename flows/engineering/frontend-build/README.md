# Frontend build

Build a frontend in a given stack with build, component-test, and accessibility evidence and an operator visual review.

The core shape is:

1. Intake design spec.
2. Plan the frontend.
3. Implement the frontend.
4. Build and typecheck.
5. Run component tests and lint.
6. Run accessibility checks.
7. Verify build evidence.
8. Visual and UX review.
9. Close out frontend.

The stack is a contract input. The deterministic gates (build, component tests, accessibility) produce honest repo-local logs; the visual and interaction quality of the UI is an explicit operator review gate, because it is judgment a static run cannot self-prove. Supported consumers: nilcore, standalone.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/frontend-build.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/webapp/frontend.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | Standalone run evidence only; other listed consumers are adapter intent. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
