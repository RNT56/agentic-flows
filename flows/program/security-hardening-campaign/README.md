# Security hardening campaign

Inventory dependency findings, fan out a bounded per-finding fix-and-verify loop, and export one audit trail for the campaign.

It combines all three composition primitives:

1. Intake and plan.
2. `flow_ref` -> `security.supply-chain-audit` (inventories findings).
3. `harden` node: `fan_out` over each finding (bounded cardinality, threshold aggregate) with a bounded `iteration` loop per finding (`until: gate:instance-hardened`).
4. `flow_ref` -> `proof.evidence-bundle-export` (exports the audit trail).
5. Verify, accept (`acceptance` gate), and close out.

This is the named `needs-spec-extension` backlog item, now unblocked: it is the first flow to combine `fan_out` + `iteration` + `flow_ref`. The per-finding fix verification is a deterministic re-scan (standalone-honest), and the campaign acceptance uses reviewer-identity. Supported consumers: crustcore, standalone (the intersection of the audit and export children's cores).

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` plus `flowctl check-composition` cover the graph, bindings, and `flow_ref` resolution. |
| Sample contract | Ready | `examples/samples/program/security-hardening-campaign.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/security-hardening-campaign.run.json` recursively validates the audit and export child run bundles. |
| Optional consumers | Preview | Standalone/CrustCore run evidence; per-finding fixes are illustrative until a runtime drives real scans. |
| Promotion gate | Open | Needs real adapter smoke evidence and a runtime that drives the child flows before `stable`. |
