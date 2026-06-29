# Backend service build

Build a scoped backend service or API in a given stack with build and test evidence and a documented API contract.

The core shape is:

1. Intake service scope.
2. Plan service architecture.
3. Implement the service.
4. Build the service.
5. Run unit and integration tests.
6. Verify and document the contract.
7. Risk review decision.
8. Close out service.

The stack is a contract input, not a separate flow per stack: the build and test gates delegate to the chosen stack's commands. Supported consumers: nilcore, crustcore, standalone.

Honesty note: the build/test gates produce honest repo-local logs; running integration tests against a live service or datastore is sandbox-class evidence a runtime must provide. Treat standalone run evidence as a contract demonstration, not proof of execution.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/backend-service.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/webapp/backend.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | Standalone run evidence only; other listed consumers are adapter intent. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
