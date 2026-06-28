# Untrusted output routing

Route model, tool, or browser output through tainting and redaction before it can influence decisions.

The core shape is:

1. Intake output.
2. Track taint.
3. Redact sensitive content.
4. Decide routing.
5. Close out routing.

Supported consumers: nilcore, crustcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/security/untrusted-output-routing.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/untrusted-output-routing.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `crustcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
