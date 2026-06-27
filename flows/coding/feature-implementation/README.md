# Feature implementation

Use this flow when an agent needs to change a repository and prove that the change satisfies the request.

The core shape is:

1. Scope the task.
2. Plan touched modules and checks.
3. Apply the patch.
4. Run focused verification.
5. Request human approval when risk requires it.
6. Close out with evidence.

NilCore should own the sandboxed work execution, CrustCore should own verifier-backed patch proof when available, and ThinClaw should own the operator-facing routine and memory of the decision.

