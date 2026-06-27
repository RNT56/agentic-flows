# CrustCore example

CrustCore can start with `flows/coding/feature-implementation/flow.yaml` if it chooses to consume this repo.

Optional adapter smoke test target:

1. Load the flow.
2. Confirm `crustcore` is in `runtime.supported_cores`.
3. Convert required `quality_gates` into verifier criteria.
4. Reject completion when `project-checks-pass` or `acceptance-covered` evidence is missing.
5. Emit events compatible with `schemas/event.schema.json`.
