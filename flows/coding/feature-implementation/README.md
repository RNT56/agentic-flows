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
