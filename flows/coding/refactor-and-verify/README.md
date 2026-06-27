# Refactor and verify

Use this flow when the goal is internal cleanup, simplification, or modularization with no intended behavior change.

The flow forces a baseline step before planning so the verifier can compare changed code against the behavior that was expected to remain stable.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/coding/refactor-and-verify.sample.json` covers required inputs and expected outputs. |
| Run evidence | Open | Needs a completed run bundle showing baseline, post-refactor checks, and equivalence evidence. |
| Optional consumers | Preview | ThinClaw, NilCore, CrustCore, and standalone support are declared as optional adapter intent. |
| Promotion gate | Open | Needs adapter smoke evidence and a real no-behavior-change run before `stable`. |
