# Consumed run bundles

These run bundles show **contract flows consumed end-to-end** through `flowctl run`
with consumer-supplied handlers. They are distinct from `examples/runs/real/`,
which holds flows that reach `status: completed` with no handler at all.

A contract flow leaves its creative core as an `agent_task` (and sometimes an
`approval`) that a consuming runtime is expected to bind. The reference runner
lets you bind those nodes at run time with `--handler node_id=command`, so the
flow runs to completion while the flow file itself stays runtime-neutral - no
agent command is baked into the flow.

## feature-implementation

`coding.feature-implementation` is the reference consumable contract. Its
`implement` node is an `agent_task` and its `approval` node is a human gate.
Bound to consumer commands, it runs to `status: completed`:

```
flowctl run flows/coding/feature-implementation/flow.yaml \
  --input "task=Add consumer handler binding to flowctl run" \
  --input "repo=." \
  --param "test_command=python -m pytest -q" \
  --handler "implement=git --no-pager diff --stat HEAD~1 HEAD" \
  --handler "approval=printf 'approved: consumer operator reviewed the change and accepted it\n'" \
  --out examples/runs/consumed/feature-implementation
```

The `test` node runs the real project checks, the `project-checks-pass` and
`acceptance-covered` gates pass from produced evidence, and both required
outputs (`patch`, `closeout`) are present. In the bundle, the `implement` and
`approval` `node.completed` events carry `handler: consumer`.

Honesty note: the handler commands here are stand-ins for what a real consumer
supplies - a coding agent for `implement`, an operator decision for `approval`.
The bundle demonstrates the **binding mechanism**, not that a coding agent ran.
A production consumer (ThinClaw, NilCore, CrustCore) binds these nodes to its
own agent and approval surfaces; the flow contract is identical.
