# Threat modeling

Use this flow to create or update a threat model for a feature, connector, or workflow: enumerate the assets, actors, trust boundaries, and abuse paths, and map each abuse path to a mitigation.

The core shape is:

1. Intake the system description and its scope and trust boundaries.
2. Enumerate assets, actors, entry points, and boundaries.
3. Analyze and rank abuse paths.
4. Verify coverage and that each abuse path maps to a mitigation.
5. Close out with the threat model and the mitigation mapping.

If those independent projects choose to consume this flow, CrustCore can treat the model as security proof input, NilCore can run the analysis in a sandboxed worker, and ThinClaw can surface mitigations as follow-ups.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/security/threat-modeling.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/threat-modeling.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | CrustCore has a repo-local contract smoke; NilCore and ThinClaw support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
