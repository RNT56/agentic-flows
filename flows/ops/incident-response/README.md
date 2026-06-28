# Incident response

Triage, mitigate, communicate, and close an incident with a declared severity and recorded timeline.

The core shape is:

1. Intake incident.
2. Declare severity.
3. Mitigate.
4. Communicate and record.
5. Verify closeout.
6. Close out incident.

Supported consumers: thinclaw, nilcore, crustcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/ops/incident-response.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/incident-response.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `thinclaw` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
