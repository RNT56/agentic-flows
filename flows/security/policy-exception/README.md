# Policy exception

Handle a request to bypass policy, sandbox, or approval with owner, expiry, risk, controls, and approval.

The core shape is:

1. Intake exception request.
2. Assess risk and controls.
3. Scope the exception.
4. Approve the exception.
5. Close out exception.

Supported consumers: thinclaw, crustcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/security/policy-exception.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/policy-exception.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `thinclaw` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
