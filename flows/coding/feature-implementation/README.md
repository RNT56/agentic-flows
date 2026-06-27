# Feature implementation

Use this flow when an agent needs to change a repository and prove that the change satisfies the request.

The core shape is:

1. Scope the task.
2. Plan touched modules and checks.
3. Apply the patch.
4. Run focused verification.
5. Request human approval when risk requires it.
6. Close out with evidence.

If those independent projects choose to consume this flow, NilCore can map the execution work to sandboxed jobs, CrustCore can map the gates to verifier-backed proof, and ThinClaw can map approvals and closeout to operator-facing routine state.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/coding/feature-implementation.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/feature-implementation.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | ThinClaw, NilCore, and CrustCore support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
