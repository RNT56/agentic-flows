# Infrastructure-as-code module

Author or change an infrastructure-as-code module with a plan diff, a policy gate, and a sandbox apply against an ephemeral environment.

The core shape is:

1. Intake infra scope.
2. Plan the change.
3. Author the module change.
4. Produce a plan diff.
5. Run policy checks.
6. Apply in a sandbox (provisions an `ephemeral-cloud-target`).
7. Destructive-change approval.
8. Close out (after teardown).

The IaC tool is selected by parameters (`plan_command`, `policy_command`), never a per-provider fork. The plan and policy gates are deterministic and standalone-honest; the `sandbox-apply-verified` gate is a `probe` whose `sandbox-run` evidence is backed by a non-self-issued `env.provisioned` event with teardown — the apply runs against an ephemeral environment, never real cloud state. Destructive or IAM-affecting changes route through an approval node. Supported consumers: nilcore.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/infra/iac-module.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/iac-module.run.json` is a NilCore run with a deterministic plan/policy gate and a `sandbox-run` apply gate backed by provisioning provenance. |
| Optional consumers | Preview | NilCore run evidence only; the sandbox apply needs a runtime that provisions an ephemeral environment. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
