# Release candidate audit

Audit a release candidate against tests, changelog, tags, and docs, confirming reproducible artifacts.

The core shape is:

1. Intake candidate.
2. Run release checks.
3. Audit artifacts.
4. Verify reproducibility.
5. Close out audit.

Supported consumers: nilcore, crustcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/proof/release-candidate-audit.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/release-candidate-audit.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `crustcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
