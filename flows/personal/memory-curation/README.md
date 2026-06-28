# Memory curation

Decide what belongs in long-term memory, with scope and retention metadata and approval for sensitive items.

The core shape is:

1. Intake candidates.
2. Classify candidates.
3. Curate memory.
4. Approve sensitive memory.
5. Close out curation.

Supported consumers: thinclaw, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/personal/memory-curation.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/memory-curation.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `thinclaw` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
