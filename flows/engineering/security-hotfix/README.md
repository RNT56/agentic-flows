# Security hotfix

Patch a vulnerability with minimal blast radius, an exploitability assessment, and a drafted advisory.

The core shape is:

1. Record vulnerability.
2. Assess exploitability.
3. Apply minimal hotfix.
4. Run checks.
5. Verify and draft advisory.
6. Approve release.
7. Close out hotfix.

Supported consumers: thinclaw, nilcore, crustcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/security-hotfix.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/security-hotfix.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `crustcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
