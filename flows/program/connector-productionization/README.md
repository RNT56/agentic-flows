# Connector productionization

Take an experimental connector to production readiness with reviewed permissions and tested failure modes.

The core shape is:

1. Intake connector.
2. Review permissions.
3. Test failure modes.
4. Check observability and docs.
5. Verify readiness.
6. Close out productionization.

Supported consumers: thinclaw, nilcore, crustcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/program/connector-productionization.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/connector-productionization.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `crustcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
