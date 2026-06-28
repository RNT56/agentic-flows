# Swarm execution

Use this flow to run multiple workers against independent slices under a concurrency cap and reconcile their outputs into one verified result.

The core shape is:

1. Intake the independent slices and the concurrency cap.
2. Plan the dispatch and slice assignments.
3. Dispatch workers under the cap.
4. Reconcile outputs with verifier proof.
5. Close out with the consolidated result and per-worker summary.

If those independent projects choose to consume this flow, NilCore can run the workers in sandboxed jobs and CrustCore can own the integration proof.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/orchestration/swarm-execution.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/swarm-execution.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | NilCore has a repo-local contract smoke; CrustCore support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
