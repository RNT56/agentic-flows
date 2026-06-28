# Dependency upgrade

Use this flow to upgrade a dependency safely: bump it, adapt the code, confirm tests pass, and record the before and after versions with a rationale.

The core shape is:

1. Intake the dependency, target version, and current version.
2. Apply the upgrade and adapt code for breaking changes.
3. Run the project checks against the upgraded dependency.
4. Verify compatibility and capture a rationale.
5. Close out with the upgrade patch and release notes.

If those independent projects choose to consume this flow, NilCore can run the upgrade in a sandboxed worker and CrustCore can map the checks to verifier-backed proof.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/dependency-upgrade.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/dependency-upgrade.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | CrustCore has a repo-local contract smoke; NilCore support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
