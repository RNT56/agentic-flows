# Supply chain audit

Use this flow to audit a project's dependencies for security advisories and license conflicts, rank the findings, and draft a remediation plan.

The core shape is:

1. Intake the dependency manifest and the license and advisory policy.
2. Build a concrete dependency inventory.
3. Assess advisories and licenses and rank findings by severity.
4. Verify every advisory cites a source and every license conflict names the dependency.
5. Close out with ranked findings and a remediation plan.

If those independent projects choose to consume this flow, NilCore can run the scan in a sandboxed worker and CrustCore can treat the findings as audit evidence.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/security/supply-chain-audit.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/supply-chain-audit.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | NilCore has a repo-local contract smoke; CrustCore support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
