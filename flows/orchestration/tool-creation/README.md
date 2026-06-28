# Tool creation

Create a new tool or adapter with a schema, a sandbox and permission profile, and failure-covering tests.

The core shape is:

1. Intake tool need.
2. Design tool schema.
3. Build the tool.
4. Test failure modes.
5. Verify schema and tests.
6. Close out tool.

Supported consumers: nilcore, crustcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/orchestration/tool-creation.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/tool-creation.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `crustcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
