# Codebase orientation

Use this flow to build a quick, verified map of an unfamiliar repository before changing it: entrypoints, tests, build commands, ownership boundaries, and risks.

The core shape is:

1. Intake the repo target and the orientation focus.
2. Scan the layout, entrypoints, and ownership boundaries.
3. Probe the build and test commands by running them.
4. Synthesize the orientation map and the verified commands.
5. Verify the map identifies the key elements.
6. Close out with the map and the commands.

If those independent projects choose to consume this flow, NilCore can run the scan and probes in a sandboxed worker.

## Runnable

This flow is **runnable** by the reference runner. The `scan` and `probe` nodes carry concrete commands (`git ls-files` and a `test_command` parameter that defaults to `pytest -q`), and the `synthesize` node carries a fallback command so the whole graph completes without a consumer-supplied agent.

Run it against any checkout:

```
flowctl run flows/research/codebase-orientation/flow.yaml \
  --input repo=. \
  --input "focus=add a new flowctl subcommand" \
  --param "test_command=pytest -q" \
  --out examples/runs/real/codebase-orientation
```

The runner executes the commands, captures their real output as artifacts, passes the `commands-verified` and `map-complete` gates from that evidence, and writes a validating run bundle. A produced example lives at `examples/runs/real/codebase-orientation/` - its `command-log` holds actual `pytest` output, not an illustration.

## Maturity rubric

| Area | Status | Evidence |
| --- | --- | --- |
| Schema validity | Ready | `flowctl validate` covers graph, contract outputs, and required gate evidence refs. |
| Sample contract | Ready | `examples/samples/research/codebase-orientation.sample.json` covers required inputs and expected outputs. |
| Run evidence | Ready | `examples/runs/codebase-orientation.run.json` includes completed gate and output evidence. |
| Real run | Ready | `examples/runs/real/codebase-orientation/` is produced by `flowctl run` with real command output. |
| Optional consumers | Preview | NilCore has a repo-local contract smoke. |
| Promotion gate | Open | Needs one real NilCore adapter smoke result before `stable`. |
