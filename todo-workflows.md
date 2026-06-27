# TODO workflows

This backlog lists novel workflows to build after the current v0.1 catalog. It is intentionally broader than the existing six reusable workflows and three templates.

Design rule: `agentic-flows` defines portable contracts; ThinClaw, NilCore, CrustCore, and standalone runners own execution. Workflows should be promoted only when they have real run evidence, adapter evidence, and machine-checkable quality gates.

## Integration model

Use this split when deciding where each workflow should run:

- ThinClaw: durable identity, memory, routines, channels, approvals, human-facing operating loops.
- NilCore: worker execution, browser or command automation, sandboxed tool use, multi-agent fan-out.
- CrustCore: verifier-owned completion, patch proof, audit evidence, approvals, policy gates.
- Standalone: local examples, templates, and low-friction flow inspection.

Every new workflow should declare:

- concrete inputs and outputs
- required capabilities
- optional consumers
- observability events
- at least one required quality gate
- evidence refs for every required gate
- a sample input and expected output
- a README maturity rubric

## Priority waves

### Wave 0: integration spine

These are not glamorous, but they make every later workflow cheaper and safer.

1. `ops.flow-intake-and-routing`
   - Purpose: turn an ambiguous user request into a selected flow, missing-context questions, and execution route.
   - Consumers: ThinClaw, NilCore, standalone.
   - Gates: selected flow is compatible with requested core; missing capabilities are explicit; user approval is captured for high-risk work.

2. `ops.capability-negotiation`
   - Purpose: compare a flow's required capabilities with a runtime's actual tools, permissions, sandbox, and approval policy.
   - Consumers: ThinClaw, NilCore, CrustCore, standalone.
   - Gates: no undeclared capability is used; unsupported capabilities fail closed.

3. `ops.event-and-evidence-bridge`
   - Purpose: convert runtime-native logs into `agentic-flows` event streams and run bundles.
   - Consumers: ThinClaw, NilCore, CrustCore.
   - Gates: event stream validates; required gate evidence maps to source flow evidence refs.

4. `ops.flow-version-upgrade`
   - Purpose: safely migrate a pinned consumer from one flow version to another.
   - Consumers: ThinClaw, NilCore, CrustCore, standalone.
   - Gates: migration steps exist; deprecated flow replacement exists; compatibility matrix is updated.

5. `ops.adapter-certification`
   - Purpose: generate adapter smoke evidence for a consumer and a flow.
   - Consumers: ThinClaw, NilCore, CrustCore.
   - Gates: loader output exists; capability check passes; run bundle validates; negative fixture fails as expected.

## P0 workflows: first real product integration

These should be built before expanding the catalog aggressively.

### ThinClaw-first workflows

1. `personal.daily-command-center`
   - Purpose: gather inboxes, calendar, routines, project signals, and pending approvals into one daily operating plan.
   - Consumers: ThinClaw primary; NilCore for delegated checks.
   - Novelty: the user starts with a verified operating plan, not a chat transcript.
   - Gates: no external action without approval; all cited items have source refs; accepted plan creates durable routine state.

2. `personal.inbox-triage-and-reply`
   - Purpose: classify messages, draft replies, identify commitments, and request approval for sends.
   - Consumers: ThinClaw primary.
   - Gates: every reply links source message ids; send action requires explicit approval; commitments become tracked tasks.

3. `personal.commitment-ledger`
   - Purpose: extract commitments from chats, email, meetings, and repo threads into a durable follow-up ledger.
   - Consumers: ThinClaw primary.
   - Gates: commitment has source, owner, due date or unknown marker, and status transition evidence.

4. `personal.memory-curation`
   - Purpose: decide what belongs in long-term memory, what should expire, and what should stay local to a project.
   - Consumers: ThinClaw primary.
   - Gates: no sensitive memory saved without approval; every memory has scope and retention metadata.

5. `personal.routine-authoring`
   - Purpose: turn repeated user behavior into a proposed ThinClaw routine.
   - Consumers: ThinClaw primary.
   - Gates: routine trigger, action, guardrails, and rollback path are present; user approves enablement.

6. `personal.cross-channel-briefing`
   - Purpose: produce a source-backed briefing across Slack, email, GitHub, calendar, and local notes.
   - Consumers: ThinClaw primary; NilCore optional for retrieval.
   - Gates: every claim has source ids; stale sources are flagged; no private content leaks into public outputs.

### NilCore-first workflows

7. `engineering.issue-to-verified-pr`
   - Purpose: take a scoped issue to branch, implementation, tests, and draft PR.
   - Consumers: NilCore primary; CrustCore for proof; ThinClaw for approval.
   - Gates: issue scope is frozen; tests pass; PR summary cites changed files and evidence.

8. `engineering.ci-failure-diagnosis`
   - Purpose: read failing CI, reproduce locally where possible, identify root cause, and propose a fix.
   - Consumers: NilCore primary; CrustCore optional for patch proof.
   - Gates: failing check id is recorded; reproduction or non-reproduction is explicit; fix evidence validates.

9. `engineering.flaky-test-stabilization`
   - Purpose: isolate flaky behavior with repeated runs, logs, and minimal stabilization patch.
   - Consumers: NilCore primary; CrustCore optional.
   - Gates: repeated-run evidence exists; root cause is distinguished from mitigation; no broad sleeps without justification.

10. `engineering.dependency-upgrade`
    - Purpose: upgrade a dependency, adapt code, check compatibility, and produce release notes.
    - Consumers: NilCore primary; CrustCore optional.
    - Gates: before/after versions recorded; tests pass; security or compatibility rationale exists.

11. `engineering.security-hotfix`
    - Purpose: patch a vulnerability with minimal blast radius and auditable proof.
    - Consumers: NilCore and CrustCore primary; ThinClaw for approval.
    - Gates: vulnerability source captured; exploitability assessment present; verifier evidence passes; release advisory drafted.

12. `engineering.browser-regression`
    - Purpose: reproduce and fix UI/browser behavior with screenshots, console logs, and deterministic assertions.
    - Consumers: NilCore primary.
    - Gates: screenshot or trace evidence exists; console errors checked; viewport coverage documented.

### CrustCore-first workflows

13. `proof.verified-patch-acceptance`
    - Purpose: decide whether a patch can be considered complete based only on verifier-owned evidence.
    - Consumers: CrustCore primary.
    - Gates: required gates have evidence; no model-authored completion claim substitutes for verifier proof.

14. `proof.patch-risk-classification`
    - Purpose: classify a patch by reversibility, policy risk, required approval, and expected verification.
    - Consumers: CrustCore primary; NilCore optional.
    - Gates: destructive paths require approval; unknown risk fails closed; policy decision is logged.

15. `proof.release-candidate-audit`
    - Purpose: audit a release candidate against tests, changelog, tags, docs, and compatibility.
    - Consumers: CrustCore primary; NilCore optional.
    - Gates: tag points at audited commit; changelog section exists; release artifacts are reproducible.

16. `proof.evidence-bundle-export`
    - Purpose: export a compact proof bundle for a completed run.
    - Consumers: CrustCore primary; standalone optional.
    - Gates: bundle includes source flow version, event stream, gate evidence, artifact refs, and verifier outcome.

## P1 workflows: coding and repo operations

17. `engineering.pr-review-and-risk-notes`
    - Purpose: review a PR for bugs, regressions, missing tests, and release risk.
    - Consumers: NilCore, CrustCore, standalone.
    - Gates: findings cite files and lines; severity is explicit; non-findings are not padded.

18. `engineering.merge-readiness`
    - Purpose: separate local state, CI state, PR review state, and merge blockers.
    - Consumers: NilCore, CrustCore, standalone.
    - Gates: no merge-ready verdict unless all required checks and reviews are green.

19. `engineering.release-train`
    - Purpose: coordinate changelog roll, tag, release package, release notes, and post-release verification.
    - Consumers: NilCore, CrustCore, standalone.
    - Gates: release check passes; tag is pushed; release artifact digest is recorded.

20. `engineering.repository-bootstrap`
    - Purpose: initialize a new repo with docs, schemas, CI, license, issue templates, and first release plan.
    - Consumers: NilCore, standalone.
    - Gates: CI passes; README explains product promise; license is present; release path is documented.

21. `engineering.monorepo-slice-execution`
    - Purpose: claim and execute a non-overlapping slice in a large repo with active parallel agents.
    - Consumers: NilCore primary; ThinClaw optional.
    - Gates: claim board checked; touched paths are scoped; conflicts are reported.

22. `engineering.large-refactor-safe-plan`
    - Purpose: split a large refactor into reversible slices with tests and rollback points.
    - Consumers: NilCore, CrustCore.
    - Gates: each slice has acceptance criteria; shared contracts are tested before behavior changes.

23. `engineering.api-contract-change`
    - Purpose: change an API contract while updating clients, docs, tests, and migration notes.
    - Consumers: NilCore, CrustCore.
    - Gates: consumers are enumerated; compatibility story exists; generated docs or schemas are updated.

24. `engineering.schema-evolution`
    - Purpose: evolve JSON Schema, database schema, or protocol contracts safely.
    - Consumers: NilCore, CrustCore.
    - Gates: migration path exists; invalid fixtures cover new failures; compatibility matrix updated.

25. `engineering.dead-code-retirement`
    - Purpose: prove code is unused, remove it, and verify behavior is unchanged.
    - Consumers: NilCore.
    - Gates: references are searched; public API impact assessed; tests pass.

26. `engineering.performance-regression`
    - Purpose: measure, isolate, and fix a performance regression with reproducible evidence.
    - Consumers: NilCore, CrustCore.
    - Gates: benchmark method recorded; variance bounded; before/after numbers included.

27. `engineering.cross-platform-regression`
    - Purpose: diagnose OS-specific failures across Linux, macOS, Windows, or ARM64.
    - Consumers: NilCore.
    - Gates: platform matrix recorded; fix is guarded by platform-specific tests or checks.

28. `engineering.docs-from-diff`
    - Purpose: detect when a code change requires docs, examples, or changelog updates.
    - Consumers: NilCore, standalone.
    - Gates: docs impact decision is explicit; affected docs updated or non-impact justified.

29. `engineering.issue-backlog-grooming`
    - Purpose: triage issues into priority, owner, reproduction status, and next action.
    - Consumers: ThinClaw, NilCore.
    - Gates: each issue receives a disposition; duplicates and blocked items cite source evidence.

30. `engineering.bug-reproduction-lab`
    - Purpose: convert a bug report into a minimal reproduction and failing test.
    - Consumers: NilCore.
    - Gates: reproduction command exists or impossibility is explained; test fails before fix.

## P1 workflows: security, trust, and compliance

31. `security.supply-chain-audit`
    - Purpose: audit dependencies, licenses, advisories, and build provenance.
    - Consumers: NilCore, CrustCore.
    - Gates: advisory sources captured; license conflicts reported; remediation PR drafted.

32. `security.secret-leak-response`
    - Purpose: detect, contain, rotate, and document a suspected secret leak.
    - Consumers: ThinClaw, NilCore, CrustCore.
    - Gates: exposed secret scope identified; rotation evidence exists; postmortem drafted.

33. `security.threat-modeling`
    - Purpose: create or update a threat model for a feature, connector, or workflow.
    - Consumers: ThinClaw, NilCore, CrustCore, standalone.
    - Gates: assets, actors, trust boundaries, abuse paths, and mitigations are enumerated.

34. `security.connector-grant-review`
    - Purpose: review a connector's requested permissions before enabling it.
    - Consumers: ThinClaw primary; CrustCore optional.
    - Gates: least-privilege decision recorded; destructive operations require approval.

35. `security.policy-exception`
    - Purpose: handle requests to bypass policy, sandbox, or approval requirements.
    - Consumers: ThinClaw, CrustCore.
    - Gates: exception has owner, expiry, risk, compensating controls, and explicit approval.

36. `security.audit-trail-reconstruction`
    - Purpose: reconstruct what happened in a run from logs, events, approvals, and artifacts.
    - Consumers: CrustCore primary; ThinClaw optional.
    - Gates: timeline is source-backed; gaps are marked; claims are not inferred as facts.

37. `security.untrusted-output-routing`
    - Purpose: route model/tool/browser output through tainting, redaction, and policy before decisions.
    - Consumers: NilCore, CrustCore.
    - Gates: tainted inputs cannot directly authorize actions; redaction evidence exists.

38. `security.access-review`
    - Purpose: periodically review user, connector, repo, and deployment permissions.
    - Consumers: ThinClaw primary.
    - Gates: every permission has owner and reason; removals and exceptions are tracked.

## P1 workflows: research and intelligence

39. `research.source-backed-brief`
    - Purpose: answer a question with citations, caveats, and confidence.
    - Consumers: ThinClaw, NilCore, standalone.
    - Gates: sources are fresh when needed; direct quotes are bounded; uncertainty is explicit.

40. `research.competitor-watch`
    - Purpose: monitor a competitor or comparable project for product, release, and positioning changes.
    - Consumers: ThinClaw, NilCore.
    - Gates: dated source evidence; changes separated from interpretation; watch cadence recorded.

41. `research.library-evaluation`
    - Purpose: decide whether to adopt a library or framework.
    - Consumers: NilCore, standalone.
    - Gates: primary docs inspected; maintenance and license checked; integration risk assessed.

42. `research.paper-to-implementation-plan`
    - Purpose: translate a paper or spec into implementable slices and validation tasks.
    - Consumers: NilCore.
    - Gates: assumptions separated from source claims; experiments and acceptance metrics defined.

43. `research.market-and-user-value`
    - Purpose: evaluate whether a product idea has real user value and differentiation.
    - Consumers: ThinClaw, standalone.
    - Gates: target user, pain, alternatives, novelty, risks, and next experiment documented.

44. `research.codebase-orientation`
    - Purpose: build a quick map of an unfamiliar repo before changing it.
    - Consumers: NilCore.
    - Gates: entrypoints, tests, build commands, ownership boundaries, and risks are identified.

45. `research.technology-radar`
    - Purpose: maintain an evolving list of technologies worth adopting, watching, or rejecting.
    - Consumers: ThinClaw.
    - Gates: each item has reason, evidence date, owner, and next review date.

## P1 workflows: operations and deployment

46. `ops.incident-response`
    - Purpose: triage, mitigate, communicate, and close an incident.
    - Consumers: ThinClaw, NilCore, CrustCore.
    - Gates: severity declared; mitigation evidence exists; timeline and follow-ups recorded.

47. `ops.deploy-and-verify`
    - Purpose: deploy a version and verify health with rollback readiness.
    - Consumers: NilCore, CrustCore.
    - Gates: preflight passes; deployment artifact identified; health checks pass; rollback plan exists.

48. `ops.rollback`
    - Purpose: safely roll back a failed deployment.
    - Consumers: NilCore, CrustCore.
    - Gates: rollback target identified; data migration risk assessed; health restored.

49. `ops.infrastructure-drift`
    - Purpose: compare intended infrastructure state to actual state and propose remediation.
    - Consumers: NilCore.
    - Gates: drift evidence captured; destructive changes require approval; remediation plan is staged.

50. `ops.backup-restore-drill`
    - Purpose: test backups by restoring into a safe environment.
    - Consumers: NilCore, CrustCore.
    - Gates: restore command recorded; data integrity checked; secrets are handled safely.

51. `ops.cost-anomaly`
    - Purpose: diagnose unexpected cloud, API, or compute spend.
    - Consumers: ThinClaw, NilCore.
    - Gates: source billing data cited; driver analysis done; recommended action has risk and owner.

52. `ops.scheduler-health`
    - Purpose: inspect recurring automations, cron jobs, reminders, and monitors for failures or drift.
    - Consumers: ThinClaw primary.
    - Gates: stale or failed schedules are surfaced; remediation is approved before changes.

## P2 workflows: product, data, and business reasoning

53. `product.kpi-diagnostics`
    - Purpose: explain why a metric changed and what to do next.
    - Consumers: ThinClaw, NilCore.
    - Gates: metric definition exists; drivers are separated from speculation; caveats included.

54. `product.experiment-readout`
    - Purpose: analyze an experiment and decide ship, iterate, or stop.
    - Consumers: NilCore, standalone.
    - Gates: sample size and guardrails reviewed; decision follows evidence.

55. `product.feedback-to-roadmap`
    - Purpose: turn user feedback into themes, opportunities, and prioritized tasks.
    - Consumers: ThinClaw.
    - Gates: feedback sources are cited; themes do not erase minority signals; priorities have rationale.

56. `product.release-positioning`
    - Purpose: produce release framing, public copy, and risk-aware rollout notes.
    - Consumers: ThinClaw, standalone.
    - Gates: claims are supported by shipped behavior; caveats and limitations are explicit.

57. `product.pricing-or-packaging-analysis`
    - Purpose: evaluate pricing, packaging, or plan changes.
    - Consumers: ThinClaw, NilCore.
    - Gates: assumptions are visible; customer impact and rollback path are documented.

58. `product.customer-success-brief`
    - Purpose: prepare a customer/account briefing from tickets, usage, docs, and roadmap.
    - Consumers: ThinClaw.
    - Gates: sensitive data scoped; open risks and asks are listed; sources are linked.

59. `product.churn-risk-review`
    - Purpose: identify churn risk and create an intervention plan.
    - Consumers: ThinClaw.
    - Gates: risk signals are source-backed; action owner and follow-up date exist.

## P2 workflows: documents, knowledge, and communication

60. `docs.operating-handbook`
    - Purpose: create or refresh a complete project operating handbook.
    - Consumers: NilCore, standalone.
    - Gates: docs index links all process docs; commands are runnable; stale claims removed.

61. `docs.api-reference-refresh`
    - Purpose: update API docs from current schemas, types, and examples.
    - Consumers: NilCore.
    - Gates: generated and hand-written docs are reconciled; examples compile or validate.

62. `docs.migration-guide`
    - Purpose: write a migration guide for breaking changes.
    - Consumers: NilCore, standalone.
    - Gates: old and new behavior compared; steps are ordered; rollback is included.

63. `docs.postmortem`
    - Purpose: produce a blameless postmortem with timeline, impact, causes, and follow-ups.
    - Consumers: ThinClaw, standalone.
    - Gates: timeline sources cited; action items have owners; unresolved unknowns are explicit.

64. `docs.decision-record`
    - Purpose: capture an architectural or product decision with alternatives and consequences.
    - Consumers: ThinClaw, standalone.
    - Gates: decision owner and date present; rejected alternatives documented.

65. `docs.public-announcement`
    - Purpose: turn shipped work into concise public-facing announcement copy.
    - Consumers: ThinClaw.
    - Gates: no unshipped claim; audience and distribution channel selected.

## P2 workflows: multi-agent orchestration

66. `orchestration.parallel-work-claiming`
    - Purpose: divide a broad objective into lanes, claim ownership, and avoid path collisions.
    - Consumers: NilCore, ThinClaw.
    - Gates: lane boundaries and dependencies explicit; active claims checked before execution.

67. `orchestration.swarm-execution`
    - Purpose: run multiple workers against independent slices and reconcile outputs.
    - Consumers: NilCore primary; CrustCore optional.
    - Gates: concurrency cap set; worker outputs summarized; integration requires verifier proof.

68. `orchestration.handoff-and-resume`
    - Purpose: compact state and hand work to another agent or future run.
    - Consumers: ThinClaw, NilCore.
    - Gates: current state, decisions, blockers, validation, and next commands are preserved.

69. `orchestration.agent-quality-review`
    - Purpose: review an agent's work for hallucinated claims, missed validation, and unsafe edits.
    - Consumers: CrustCore, standalone.
    - Gates: findings cite evidence; false positives are avoided; residual risk is explicit.

70. `orchestration.self-improvement-loop`
    - Purpose: identify repeated failures and propose improvements to prompts, tools, skills, or workflows.
    - Consumers: ThinClaw, NilCore, CrustCore.
    - Gates: repeated pattern evidence exists; improvement is tested; rollout is reversible.

71. `orchestration.tool-creation`
    - Purpose: create a new tool or adapter when existing tools are inadequate.
    - Consumers: NilCore, CrustCore.
    - Gates: tool schema exists; sandbox and permission profile declared; tests cover failures.

72. `orchestration.skill-authoring`
    - Purpose: turn repeated domain knowledge into a reusable skill or guide.
    - Consumers: ThinClaw, NilCore.
    - Gates: trigger conditions, instructions, assets, and validation examples exist.

## P3 workflows: long-horizon autonomous programs

73. `program.repo-maintenance-autopilot`
    - Purpose: continuously detect small maintenance work, batch it safely, and open verified PRs.
    - Consumers: ThinClaw, NilCore, CrustCore.
    - Gates: task selection is bounded; each PR has focused scope; CI and verifier evidence pass.

74. `program.product-release-autopilot`
    - Purpose: move a product from backlog to release notes through implementation, QA, docs, and rollout.
    - Consumers: ThinClaw, NilCore, CrustCore.
    - Gates: roadmap item linked; acceptance gates pass; rollout and rollback are planned.

75. `program.research-to-roadmap`
    - Purpose: convert ongoing research signals into a prioritized roadmap.
    - Consumers: ThinClaw, NilCore.
    - Gates: source evidence fresh; opportunities ranked; next experiments defined.

76. `program.security-hardening-campaign`
    - Purpose: run a bounded security hardening campaign across repos.
    - Consumers: ThinClaw, NilCore, CrustCore.
    - Gates: inventory complete; fixes are sliced; audit trail exported.

77. `program.connector-productionization`
    - Purpose: take an experimental connector to production readiness.
    - Consumers: ThinClaw, NilCore, CrustCore.
    - Gates: permissions reviewed; failure modes tested; observability and docs complete.

78. `program.knowledge-base-maintenance`
    - Purpose: keep docs, memory, decisions, and examples current across a project family.
    - Consumers: ThinClaw, NilCore.
    - Gates: stale items detected; updates cite sources; deletions are conservative.

## Integration milestones

### Milestone A: first integrated loop

Build one complete loop across all three independent projects:

- ThinClaw loads `personal.daily-command-center`.
- NilCore executes delegated checks from the plan.
- CrustCore verifies completion evidence for any code or deployment change.
- `agentic-flows` receives a valid run bundle and event stream.

Exit criteria:

- a real flow is pinned by tag
- runtime emits valid events
- adapter smoke manifest points at real evidence
- run bundle validates in this repo

### Milestone B: stable promotion candidate

Pick one preview flow and make it stable.

Best candidates:

- `general.human-in-the-loop-review`
- `coding.feature-implementation`
- `coding.refactor-and-verify`

Exit criteria:

- every declared optional consumer has adapter evidence
- run bundle evidence exists for at least one real run
- compatibility matrix is updated
- changelog documents stability promotion

### Milestone C: verified autonomous work platform

Use the catalog to prove a higher-level thesis:

- ThinClaw owns user intent, schedule, memory, and approvals.
- NilCore owns delegated execution and sandboxed automation.
- CrustCore owns verifier-backed completion and proof.
- `agentic-flows` owns the reusable workflow contract.

Exit criteria:

- at least one end-to-end program workflow runs across the stack
- every action has event evidence
- every completion claim has verifier-owned proof
- user-facing summaries stay source-backed

## Build order recommendation

1. `ops.flow-intake-and-routing`
2. `ops.capability-negotiation`
3. `ops.event-and-evidence-bridge`
4. `personal.daily-command-center`
5. `engineering.issue-to-verified-pr`
6. `proof.verified-patch-acceptance`
7. `engineering.ci-failure-diagnosis`
8. `engineering.pr-review-and-risk-notes`
9. `engineering.release-train`
10. `orchestration.parallel-work-claiming`
11. `security.supply-chain-audit`
12. `ops.incident-response`
13. `research.source-backed-brief`
14. `program.repo-maintenance-autopilot`
15. `program.product-release-autopilot`

This order builds the contract spine first, then useful daily workflows, then higher-autonomy programs.

## Do not build yet

Avoid these until the integration spine is proven:

- flows that assume ThinClaw, NilCore, and CrustCore share one runtime
- flows that perform irreversible actions without approval nodes
- flows that call a task complete based on model text instead of verifier evidence
- flows with vague outputs such as "report" or "done" without evidence refs
- flows that cannot emit useful run events
- stable workflows without real adapter evidence

