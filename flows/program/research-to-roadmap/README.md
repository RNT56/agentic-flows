# Research to roadmap

Convert ongoing research signals into a ranked roadmap with fresh sources and defined next experiments.

The core shape is:

1. Intake signals.
2. Digest signals.
3. Rank opportunities.
4. Verify the roadmap.
5. Close out roadmap.

Supported consumers: thinclaw, nilcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/program/research-to-roadmap.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/research-to-roadmap.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `thinclaw` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
