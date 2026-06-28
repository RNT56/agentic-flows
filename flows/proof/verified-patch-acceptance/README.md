# Verified patch acceptance

Use this flow when completion must be decided by a verifier, not asserted by a model. It accepts a patch only when every required gate has passing, cited evidence, and fails closed otherwise.

The core shape is:

1. Intake the patch and the required gates and acceptance criteria.
2. Run the verifier-owned checks against the patch.
3. Collect gate evidence and form an evidence-backed verdict.
4. Accept only on complete passing evidence, otherwise reject and fail closed.
5. Close out with the verdict and a proof report.

If those independent projects choose to consume this flow, CrustCore can own the verdict as verifier-owned proof; standalone runners can inspect the verdict and its cited evidence directly. The completion claim never substitutes for verifier evidence.

## Runnable

This flow is **runnable** by the reference runner: its `checks` tool node runs the verifier-owned command. Run it against this repo, pointing the check at the test suite:

```
flowctl run flows/proof/verified-patch-acceptance/flow.yaml \
  --input "patch=HEAD" \
  --input "acceptance_criteria=All tracked tests pass and the run bundle validates." \
  --param "test_command=python -m pytest -q" \
  --out examples/runs/real/verified-patch-acceptance
```

The runner runs the checks, captures the real test output as the `test-log` artifact, passes the `verifier-checks-pass` and `verdict-present` gates from that evidence, and writes a validating run bundle. A produced example lives at `examples/runs/real/verified-patch-acceptance/`. The default `test_command` is a portable fallback chain; pass the project's actual check command as shown.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/proof/verified-patch-acceptance.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/verified-patch-acceptance.run.json` includes completed gate and output evidence. |
| Real run | Ready | `examples/runs/real/verified-patch-acceptance/` is produced by `flowctl run` with real test output. |
| Optional consumers | Preview | CrustCore has a repo-local contract smoke; standalone inspection is supported directly. |
| Promotion gate | Open | Needs one real CrustCore adapter smoke result before `stable`. |
