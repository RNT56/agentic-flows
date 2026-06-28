# Technology radar

Place technologies into adopt, watch, or reject with a reason, evidence date, owner, and next review date.

The core shape is:

1. Intake technologies.
2. Assess technologies.
3. Place on radar.
4. Verify entries.
5. Close out radar.

Supported consumers: thinclaw, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/research/technology-radar.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/technology-radar.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `thinclaw` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
