# Issue to verified PR

Use this flow to take a scoped issue all the way to a draft pull request whose summary cites the changed files and the validation evidence behind it.

The core shape is:

1. Intake and freeze the issue scope.
2. Plan touched modules and the verification strategy.
3. Implement the change on a branch.
4. Run focused checks.
5. Request human approval when behavior, public API, or deployment risk changed.
6. Draft a PR summary that cites changed files and evidence.

If those independent projects choose to consume this flow, NilCore can run the implementation in a sandboxed worker, CrustCore can map the gates to verifier-backed proof, and ThinClaw can map approval and PR closeout to operator-facing routine state.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/engineering/issue-to-verified-pr.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/issue-to-verified-pr.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | NilCore has a repo-local contract smoke; CrustCore and ThinClaw support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
