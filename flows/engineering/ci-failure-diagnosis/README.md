# CI failure diagnosis

Use this flow to turn a failing CI check into a root-cause diagnosis and a proposed fix, with an explicit record of whether the failure reproduced locally.

The core shape is:

1. Record the failing check id and its logs.
2. Attempt to reproduce the failure locally.
3. Decide reproduced or not, and record the root cause direction.
4. Verify a proposed fix against the failure.
5. Close out with the diagnosis and the fix proposal or a no-fix statement.

If those independent projects choose to consume this flow, NilCore can run reproduction in a sandboxed worker and CrustCore can map the fix evidence to verifier-backed proof.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/ci-failure-diagnosis.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/ci-failure-diagnosis.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | NilCore has a repo-local contract smoke; CrustCore support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
