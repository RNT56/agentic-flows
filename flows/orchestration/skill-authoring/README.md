# Skill authoring

Turn repeated domain knowledge into a reusable skill with triggers, instructions, assets, and examples.

The core shape is:

1. Intake knowledge.
2. Author the skill.
3. Add validation examples.
4. Verify the skill.
5. Close out skill.

Supported consumers: thinclaw, nilcore, standalone. Independent projects may map the nodes onto their own execution, sandbox, approval, or proof surfaces; nothing here assumes a shared runtime.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/orchestration/skill-authoring.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/skill-authoring.run.json` includes completed gate and output evidence. |
| Optional consumers | Preview | `thinclaw` has a repo-local contract smoke; other listed consumers are optional adapter intent only. |
| Promotion gate | Open | Needs one real adapter smoke result per listed optional consumer before `stable`. |
