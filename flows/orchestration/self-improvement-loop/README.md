# Self improvement loop

Identify repeated failures and propose a tested, reversible improvement to prompts, tools, or workflows.

The core shape is:

1. Intake failures.
2. Detect repeated pattern.
3. Propose improvement.
4. Test the improvement.
5. Verify and plan rollout.
6. Close out improvement.

Supported consumers: thinclaw, nilcore, crustcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/orchestration/self-improvement-loop.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/self-improvement-loop.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `crustcore` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
