# Flaky test stabilization

Use this flow to isolate a flaky test with repeated runs and logs, then apply a minimal change that addresses the root cause rather than masking it.

The core shape is:

1. Intake the flaky test id and the repo target.
2. Run the test repeatedly to capture the flaky behavior.
3. Find the root cause, distinguished from a mitigation.
4. Apply the smallest stabilization.
5. Verify repeated-run evidence exists and the change targets the root cause.
6. Close out with the stabilization patch and the analysis.

If those independent projects choose to consume this flow, NilCore can run the repeated executions in a sandboxed worker.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/flaky-test-stabilization.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/flaky-test-stabilization.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | NilCore has a repo-local contract smoke. |
| Promotion gate | Open | Needs one real NilCore adapter smoke result before `stable`. |
