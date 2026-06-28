# Goals

## Mission

`agentic-flows` is a **library of runnable, consumable agentic workflows** for RNT56 agentic projects.

A flow is not just a diagram of steps. Each flow carries enough **portable substance** to actually be run and to deliver value: concrete instructions for each step, structured per-node inputs and outputs, parameters, concrete checks and commands, quality gates, and an evidence contract. A consuming runtime — or the bundled reference runner — can load a flow and **execute it to a real result with real evidence**, not a placeholder.

Execution still happens in a runtime. The runtimes own the heavy machinery (sandbox, permissions, secrets, tool implementations, approval UX). `agentic-flows` owns the part that is worth sharing: the *workflow itself* — the instructions, contracts, checks, and gates — packaged so that any consumer runs the same vetted workflow the same way and can prove it ran.

| Consumer | Role |
| --- | --- |
| ThinClaw | durable routines, operator control, approvals |
| NilCore | worker and supervisor execution, sandboxed tools |
| CrustCore | verifier-owned proof and completion |
| Reference runner (`flowctl run`) | execute runnable flows locally and emit real run evidence |

## What "consumable" means

A flow is consumable when a runtime can load it and execute it without the runtime author having to re-invent the workflow. Concretely, a consumable flow provides:

1. **Instructions** — what each step must actually do (the prompt/guidance for an `agent_task`, the criteria for a `verifier`, the action for a `tool`).
2. **Structured I/O** — each node declares its inputs and outputs by name and type, so a runtime can wire steps together mechanically.
3. **Parameters** — typed, defaulted knobs a consumer can set without editing the flow.
4. **Concrete checks** — `tool`/`verifier` nodes carry the actual command or check to run.
5. **Quality gates with evidence** — completion rests on machine-checkable gates backed by named evidence.
6. **Failure handling** — declared retry/abort/escalate behavior.
7. **A worked example and, for runnable flows, real produced evidence.**

The **runtime still supplies the bindings** that cannot be portable: which agent model, the sandbox, repo credentials, secrets, the concrete tool runtime, and the approval surface. Those live in `runtime.adapter_hints` and in the consumer, never hard-coded into the portable flow.

## Flow maturity: contract vs runnable

| Kind | Meaning |
| --- | --- |
| `contract` | The flow carries the portable substance (instructions, I/O, gates) but its steps depend on a consumer-provided handler (an agent or external tool) to execute. |
| `runnable` | The flow can be executed end to end by the bundled reference runner using only local handlers (command and data steps), producing a real run bundle with real artifacts. |

Both are first-class. `runnable` flows are how we prove the model end to end with real evidence; `contract` flows are consumed by a runtime that supplies the missing handlers.

## Primary goals

1. Define workflows that are substantive enough to run, not just diagrams of steps.
2. Carry per-node instructions, structured I/O, parameters, concrete commands, gates, and failure handling in a stable, human-readable format.
3. Ship a reference runner (`flowctl run`) that executes runnable flows and emits real run evidence.
4. Validate flow structure, graph semantics, node substance, event evidence, and compatibility.
5. Keep runtime-specific bindings (sandbox, secrets, tool/agent implementations, approval UX) in the consumer and `adapter_hints`, never hard-coded into the portable flow.
6. Provide adapter contracts for ThinClaw, NilCore, and CrustCore without claiming they are integrated.
7. Maintain a release process that lets consuming projects pin compatible versions.

## Non-goals

- This repo does not own sandboxing, permissions, secrets, memory, or approval UX — those belong to the consuming runtime.
- The reference runner is a minimal, auditable executor for runnable flows, not a production workflow engine or scheduler.
- This repo does not replace ThinClaw, NilCore, or CrustCore, and does not assume they share APIs or runtime state.
- This repo should not hard-code runtime-specific tool implementations, credentials, or endpoints into a portable flow.
- This repo should not ship thin, look-alike flows that carry no instructions, I/O, or checks; breadth without substance is not a goal.
- This repo should not mark a flow `stable` without real run evidence and adapter evidence from each declared optional consumer.

## Success metrics

- Every flow under `flows/` validates in CI, including its substance layer.
- Every reusable flow declares per-node instructions or a concrete command, structured node I/O, and required quality gates.
- Every `runnable` flow has a real run bundle produced by `flowctl run` (real artifacts, not placeholder URIs).
- Every `stable` flow has real run evidence and adapter smoke evidence for each declared optional consumer.
- Consuming repos can pin a tag and execute a flow with only consumer-provided handlers for `agent_task`/`approval` steps.

## Operating principles

- Substance first: a flow must carry what a consumer needs to run it, not just the shape.
- Real evidence over assertion: prefer a produced run bundle to a hand-written one; never describe a flow as runnable without a real run.
- Portable by default, bound at the edge: instructions and contracts are portable; sandbox, secrets, and concrete tool/agent implementations bind in the consumer.
- Depth over breadth: a few deeply specified, runnable flows beat many thin look-alikes.
- Explicit compatibility: never imply support for a core that has not loaded and run the flow.
