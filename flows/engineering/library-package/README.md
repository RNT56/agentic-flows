# Library package build

Build a reusable library package in a given ecosystem to publish-ready state with build, test, and reviewed public-API and semver evidence.

The core shape is:

1. Intake package scope.
2. Plan the package.
3. Implement the library.
4. Build and test.
5. Compute the public-API diff and semver bump.
6. Public-API review.
7. Close out (publish-ready; no publish in-flow).

The ecosystem is a contract input and the build/test commands are parameters. The `public-api-reviewed` gate is a `judgment` gate where the reviewer must not be a producing agent — semver and public-API impact is exactly the call no author should self-certify. The flow deliberately stops at publish-ready; the irreversible publish action is out of scope. Supported consumers: nilcore, standalone.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/library-package.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/library-package.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | Standalone run evidence (deterministic + judgment); other listed consumers are adapter intent. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
