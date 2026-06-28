# Source-backed brief

Use this flow to answer a question with a short, cited brief: every claim maps to a source, quotes are bounded, and uncertainty and freshness are explicit.

The core shape is:

1. Intake the question and the source constraints.
2. Gather candidate sources within scope.
3. Synthesize the answer, mapping each claim to a citation.
4. Verify citations, bounded quotes, and explicit uncertainty.
5. Close out with the cited brief and the citation list.

If those independent projects choose to consume this flow, ThinClaw can deliver the brief as an operator-facing briefing and NilCore can run retrieval in a sandboxed worker.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/research/source-backed-brief.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/source-backed-brief.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | ThinClaw has a repo-local contract smoke; NilCore support is declared as optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
