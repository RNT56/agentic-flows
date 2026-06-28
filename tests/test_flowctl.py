from pathlib import Path

import json

from flowctl.cli import (
    DEFAULT_ADAPTER_SMOKE_SCHEMA,
    DEFAULT_EVENT_SCHEMA,
    DEFAULT_EVENT_STREAM_SCHEMA,
    DEFAULT_RUN_SCHEMA,
    DEFAULT_SAMPLE_SCHEMA,
    DEFAULT_SCHEMA,
    build_replay_summary,
    build_report_summary,
    collect_release_package_files,
    dump_yaml,
    execution_order,
    find_adapter_smoke_files,
    find_event_stream_files,
    find_flow_files,
    find_json_files,
    find_markdown_files,
    find_run_files,
    find_sample_files,
    load_json,
    load_yaml,
    normalize_flow_document,
    parse_kv_list,
    run_flow,
    substitute_command,
    validate_adapter_smoke_document,
    validate_event_document,
    validate_event_stream_document,
    validate_flow_document,
    validate_changelog,
    validate_markdown_links,
    validate_release_readiness,
    validate_run_document,
    validate_sample_document,
)


def test_repository_flows_are_valid() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    failures: list[str] = []

    for path in find_flow_files([]):
        errors = validate_flow_document(load_yaml(path), schema)
        if errors:
            failures.append(f"{path}: {errors}")

    assert failures == []


def test_repository_flows_are_normalized() -> None:
    failures: list[str] = []

    for path in find_flow_files([]):
        document = load_yaml(path)
        normalized = dump_yaml(normalize_flow_document(document))
        if path.read_text(encoding="utf-8") != normalized:
            failures.append(str(path))

    assert failures == []


def test_missing_edge_target_is_rejected() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    invalid = load_yaml(Path("tests/fixtures/invalid-missing-node.yaml"))

    errors = validate_flow_document(invalid, schema)

    assert any("references missing node 'verify'" in error for error in errors)


def test_missing_required_output_is_rejected() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    invalid = load_yaml(Path("tests/fixtures/invalid-missing-output.yaml"))

    errors = validate_flow_document(invalid, schema)

    assert any("required output is not produced" in error for error in errors)


def test_missing_node_requirement_is_rejected() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    invalid = load_yaml(Path("tests/fixtures/invalid-missing-requirement.yaml"))

    errors = validate_flow_document(invalid, schema)

    assert any("'never-produced' is not produced" in error for error in errors)


def test_undeclared_gate_evidence_ref_is_rejected() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    invalid = load_yaml(Path("tests/fixtures/invalid-gate-evidence-ref.yaml"))

    errors = validate_flow_document(invalid, schema)

    assert any("'undeclared-proof' is not declared" in error for error in errors)


def test_semantic_validation_fixture_coverage() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    cases = [
        ("tests/fixtures/invalid-command-gate-missing-command.yaml", "command gates require a command"),
        ("tests/fixtures/invalid-deprecated-missing-migration.yaml", "deprecated flows require migration guidance"),
        ("tests/fixtures/invalid-duplicate-node.yaml", "duplicate node id 'intake'"),
        ("tests/fixtures/invalid-entrypoint.yaml", "references missing node 'missing'"),
        ("tests/fixtures/invalid-migration-missing-deprecated-by.yaml", "migration guidance requires deprecated_by"),
        ("tests/fixtures/invalid-no-required-gate.yaml", "at least one gate must be required"),
        ("tests/fixtures/invalid-required-gate-missing-evidence-ref.yaml", "required gates need at least one evidence reference"),
        ("tests/fixtures/invalid-unreachable-node.yaml", "node 'orphan' is not reachable"),
    ]

    for fixture, expected in cases:
        errors = validate_flow_document(load_yaml(Path(fixture)), schema)
        assert any(expected in error for error in errors), (fixture, errors)


def test_sample_event_matches_event_schema() -> None:
    schema = load_json(Path("schemas/event.schema.json"))
    with Path("examples/standalone/event.sample.json").open("r", encoding="utf-8") as handle:
        event = json.load(handle)

    errors = validate_event_document(event, schema)

    assert errors == []


def test_invalid_event_is_rejected() -> None:
    schema = load_json(Path("schemas/event.schema.json"))
    invalid = load_json(Path("tests/fixtures/invalid-event.json"))

    errors = validate_event_document(invalid, schema)

    assert any("$.timestamp" in error for error in errors)
    assert any("$.severity" in error for error in errors)


def test_event_discovery_excludes_run_bundles() -> None:
    paths = find_json_files([Path("examples")])

    assert Path("examples/standalone/event.sample.json").resolve() in paths
    assert Path("examples/runs/feature-implementation.run.json").resolve() not in paths
    assert Path("examples/adapters/thinclaw-human-review.adapter-smoke.json").resolve() not in paths
    assert Path("examples/samples/coding/feature-implementation.sample.json").resolve() not in paths
    assert Path("examples/streams/feature-implementation/feature-implementation.stream.json").resolve() not in paths
    assert Path("examples/streams/feature-implementation/events/001-flow-started.json").resolve() in paths
    # Run-bundle artifacts (intake records, command logs) are not standalone events.
    assert (
        Path("examples/runs/real/codebase-orientation/artifacts/orientation-request.json").resolve()
        not in paths
    )


def test_adapter_smoke_discovery_finds_manifests() -> None:
    paths = find_adapter_smoke_files([Path("examples/adapters")])

    assert Path("examples/adapters/thinclaw-human-review.adapter-smoke.json").resolve() in paths


def test_event_stream_discovery_finds_stream_manifests() -> None:
    paths = find_event_stream_files([Path("examples/streams")])

    assert Path("examples/streams/feature-implementation/feature-implementation.stream.json").resolve() in paths


def test_sample_discovery_finds_flow_samples() -> None:
    paths = find_sample_files([Path("examples/samples")])

    assert Path("examples/samples/coding/feature-implementation.sample.json").resolve() in paths


def test_sample_run_bundle_is_valid() -> None:
    run_schema = load_json(Path("schemas/run.schema.json"))
    event_schema = load_json(Path("schemas/event.schema.json"))
    flow_schema = load_json(DEFAULT_SCHEMA)
    run = load_json(Path("examples/runs/feature-implementation.run.json"))

    errors = validate_run_document(
        run,
        run_schema,
        event_schema,
        flow_schema,
        run_path=Path("examples/runs/feature-implementation.run.json"),
    )

    assert errors == []


def test_repository_run_bundles_are_valid() -> None:
    run_schema = load_json(Path("schemas/run.schema.json"))
    event_schema = load_json(Path("schemas/event.schema.json"))
    flow_schema = load_json(DEFAULT_SCHEMA)
    failures: list[str] = []

    for path in find_run_files([Path("examples/runs")]):
        errors = validate_run_document(load_json(path), run_schema, event_schema, flow_schema, run_path=path)
        if errors:
            failures.append(f"{path}: {errors}")

    assert failures == []


def test_repository_event_streams_are_valid() -> None:
    stream_schema = load_json(DEFAULT_EVENT_STREAM_SCHEMA)
    event_schema = load_json(Path("schemas/event.schema.json"))
    flow_schema = load_json(DEFAULT_SCHEMA)
    failures: list[str] = []

    for path in find_event_stream_files([Path("examples/streams")]):
        errors = validate_event_stream_document(
            load_json(path),
            stream_schema,
            event_schema,
            flow_schema,
            stream_path=path,
        )
        if errors:
            failures.append(f"{path}: {errors}")

    assert failures == []


def test_repository_adapter_smokes_are_valid() -> None:
    adapter_schema = load_json(DEFAULT_ADAPTER_SMOKE_SCHEMA)
    flow_schema = load_json(DEFAULT_SCHEMA)
    run_schema = load_json(Path("schemas/run.schema.json"))
    event_schema = load_json(Path("schemas/event.schema.json"))
    stream_schema = load_json(DEFAULT_EVENT_STREAM_SCHEMA)
    failures: list[str] = []

    for path in find_adapter_smoke_files([Path("examples/adapters")]):
        errors = validate_adapter_smoke_document(
            load_json(path),
            adapter_schema,
            flow_schema,
            run_schema,
            event_schema,
            stream_schema,
            adapter_path=path,
        )
        if errors:
            failures.append(f"{path}: {errors}")

    assert failures == []


def test_run_bundle_replay_summary_reconstructs_gates() -> None:
    run = load_json(Path("examples/runs/feature-implementation.run.json"))

    summary = build_replay_summary(run)

    assert summary["run"]["id"] == "run-feature-implementation-0001"
    assert summary["flow"]["id"] == "coding.feature-implementation"
    assert summary["outputs"] == ["closeout", "patch"]
    assert summary["gates"][0]["gate_id"] == "project-checks-pass"
    assert "test-log" in summary["gates"][0]["evidence_refs"]


def test_flow_samples_are_valid() -> None:
    sample_schema = load_json(Path("schemas/sample.schema.json"))
    flow_schema = load_json(DEFAULT_SCHEMA)
    failures: list[str] = []

    for path in find_sample_files([Path("examples/samples")]):
        errors = validate_sample_document(load_json(path), sample_schema, flow_schema, sample_path=path)
        if errors:
            failures.append(f"{path}: {errors}")

    assert failures == []


def test_changelog_structure_is_valid() -> None:
    errors = validate_changelog(Path("CHANGELOG.md"))

    assert errors == []


def test_repository_markdown_links_are_valid() -> None:
    failures: list[str] = []

    for path in find_markdown_files([]):
        errors = validate_markdown_links(path)
        if errors:
            failures.append(f"{path}: {errors}")

    assert failures == []


def test_release_package_file_set_contains_contract_assets() -> None:
    files = {path.relative_to(Path.cwd()).as_posix() for path in collect_release_package_files([])}

    assert "schemas/flow.schema.json" in files
    assert "schemas/adapter-smoke.schema.json" in files
    assert "flows/coding/feature-implementation/flow.yaml" in files
    assert "templates/coding-feature/flow.yaml" in files
    assert "examples/samples/coding/feature-implementation.sample.json" in files
    assert "LICENSE" in files


def release_check_schemas() -> tuple[dict, dict, dict, dict, dict, dict]:
    return (
        load_json(DEFAULT_SCHEMA),
        load_json(DEFAULT_ADAPTER_SMOKE_SCHEMA),
        load_json(DEFAULT_RUN_SCHEMA),
        load_json(DEFAULT_EVENT_SCHEMA),
        load_json(DEFAULT_EVENT_STREAM_SCHEMA),
        load_json(DEFAULT_SAMPLE_SCHEMA),
    )


def test_repository_release_readiness_is_valid() -> None:
    errors = validate_release_readiness(find_flow_files([]), *release_check_schemas())

    assert errors == []


def test_release_check_rejects_missing_deprecation_target(tmp_path: Path) -> None:
    flow = load_yaml(Path("flows/coding/feature-implementation/flow.yaml"))
    flow["deprecated_by"] = "coding.future-replacement"
    flow["migration"] = {
        "summary": "Move to the future replacement flow once it exists.",
        "steps": ["Pin the replacement flow and update the consumer mapping."],
    }
    flow_path = tmp_path / "flow.yaml"
    flow_path.write_text(dump_yaml(flow), encoding="utf-8")

    errors = validate_release_readiness([flow_path], *release_check_schemas())

    assert any(
        "replacement flow 'coding.future-replacement' is not in the release catalog" in error
        for error in errors
    )


def test_release_check_rejects_stable_flow_missing_consumer_evidence(tmp_path: Path) -> None:
    source_flow = Path("flows/coding/feature-implementation/flow.yaml")
    flow = load_yaml(source_flow)
    flow["stability"] = "stable"
    flow_path = tmp_path / "flow.yaml"
    flow_path.write_text(dump_yaml(flow), encoding="utf-8")
    source_readme = source_flow.with_name("README.md").read_text(encoding="utf-8")
    (tmp_path / "README.md").write_text(source_readme, encoding="utf-8")

    errors = validate_release_readiness([flow_path], *release_check_schemas())

    assert any("adapter smoke evidence for nilcore" in error for error in errors)
    assert any("adapter smoke evidence for thinclaw" in error for error in errors)


def test_sample_unknown_output_is_rejected() -> None:
    sample_schema = load_json(Path("schemas/sample.schema.json"))
    flow_schema = load_json(DEFAULT_SCHEMA)
    invalid = load_json(Path("tests/fixtures/invalid-sample-unknown-output.json"))

    errors = validate_sample_document(
        invalid,
        sample_schema,
        flow_schema,
        sample_path=Path("tests/fixtures/invalid-sample-unknown-output.json"),
    )

    assert any("$.expected_outputs.unexpected" in error for error in errors)


def test_run_bundle_missing_required_gate_is_rejected() -> None:
    run_schema = load_json(Path("schemas/run.schema.json"))
    event_schema = load_json(Path("schemas/event.schema.json"))
    flow_schema = load_json(DEFAULT_SCHEMA)
    run = load_json(Path("tests/fixtures/invalid-run-missing-gate.json"))

    errors = validate_run_document(
        run,
        run_schema,
        event_schema,
        flow_schema,
        run_path=Path("tests/fixtures/invalid-run-missing-gate.json"),
    )

    assert any("required quality gate 'project-checks-pass'" in error for error in errors)
    assert any("$.outputs.patch" in error for error in errors)


def test_run_bundle_wrong_gate_evidence_ref_is_rejected() -> None:
    run_schema = load_json(Path("schemas/run.schema.json"))
    event_schema = load_json(Path("schemas/event.schema.json"))
    flow_schema = load_json(DEFAULT_SCHEMA)
    run = load_json(Path("tests/fixtures/invalid-run-wrong-gate-evidence.json"))

    errors = validate_run_document(
        run,
        run_schema,
        event_schema,
        flow_schema,
        run_path=Path("tests/fixtures/invalid-run-wrong-gate-evidence.json"),
    )

    assert any("needs evidence id or kind matching one of: test-log" in error for error in errors)


def test_event_stream_version_mismatch_is_rejected() -> None:
    stream_schema = load_json(DEFAULT_EVENT_STREAM_SCHEMA)
    event_schema = load_json(Path("schemas/event.schema.json"))
    flow_schema = load_json(DEFAULT_SCHEMA)
    stream = load_json(Path("tests/fixtures/invalid-event-stream-version-mismatch.stream.json"))

    errors = validate_event_stream_document(
        stream,
        stream_schema,
        event_schema,
        flow_schema,
        stream_path=Path("tests/fixtures/invalid-event-stream-version-mismatch.stream.json"),
    )

    assert any("$.flow.version: does not match source flow version" in error for error in errors)
    assert any("$.events[0].flow_version: does not match run flow version" in error for error in errors)


def test_report_summary_counts_stability_and_cores() -> None:
    summary = build_report_summary(
        [
            {"stability": "preview", "valid": True, "issues": [], "supported_cores": ["standalone", "nilcore"]},
            {"stability": "experimental", "valid": True, "issues": ["needs README"], "supported_cores": ["standalone"]},
        ]
    )

    assert summary["total"] == 2
    assert summary["valid"] == 2
    assert summary["with_issues"] == 1
    assert summary["by_stability"] == {"experimental": 1, "preview": 1}
    assert summary["by_optional_consumer"] == {"nilcore": 1, "standalone": 2}


def test_parse_kv_list_parses_pairs_and_rejects_bare_tokens() -> None:
    assert parse_kv_list(["a=1", "b=two=three"]) == {"a": "1", "b": "two=three"}
    try:
        parse_kv_list(["nope"])
    except ValueError as exc:
        assert "key=value" in str(exc)
    else:  # pragma: no cover - guard against silent acceptance
        raise AssertionError("expected ValueError for bare token")


def test_substitute_command_fills_params_and_inputs_and_keeps_unknown() -> None:
    rendered = substitute_command(
        "run ${param.cmd} on ${input.repo} keep ${param.missing}",
        {"cmd": "pytest -q"},
        {"repo": "."},
    )
    assert rendered == "run pytest -q on . keep ${param.missing}"


def test_execution_order_respects_produces_requires_dependencies() -> None:
    document = {
        "nodes": [
            {"id": "final", "type": "finalizer", "requires": ["log"], "produces": ["result"]},
            {"id": "probe", "type": "tool", "produces": ["log"]},
            {"id": "intake", "type": "intake", "produces": ["req"]},
        ]
    }
    order = [node["id"] for node in execution_order(document)]
    assert order.index("probe") < order.index("final")


def _minimal_runnable_flow() -> dict:
    return {
        "spec_version": "agentic-flows/v1",
        "id": "test.runner-smoke",
        "version": "0.1.0",
        "title": "Runner smoke",
        "summary": "Minimal runnable flow exercised by the reference runner test.",
        "stability": "experimental",
        "owners": ["RNT56"],
        "tags": ["test"],
        "entrypoint": "intake",
        "runtime": {"supported_cores": ["standalone"], "required_capabilities": ["command.run"]},
        "contracts": {
            "inputs": [{"id": "repo", "type": "uri", "required": True}],
            "outputs": [{"id": "result", "type": "markdown", "required": True}],
            "artifacts": ["probe-log"],
        },
        "nodes": [
            {"id": "intake", "type": "intake", "title": "Intake", "description": "Capture the inputs.", "produces": ["req"]},
            {
                "id": "probe",
                "type": "tool",
                "title": "Probe command",
                "description": "Run a harmless command and capture output.",
                "command": "printf 'hello from ${param.token}'",
                "parameters": [{"id": "token", "type": "text", "required": False, "default": "runner"}],
                "produces": ["probe-log"],
                "on_failure": {"action": "abort"},
            },
            {
                "id": "final",
                "type": "finalizer",
                "title": "Close out",
                "description": "Return the result for the run.",
                "requires": ["probe-log"],
                "produces": ["result"],
            },
        ],
        "edges": [
            {"from": "intake", "to": "probe"},
            {"from": "probe", "to": "final"},
        ],
        "quality_gates": [
            {
                "id": "probe-passed",
                "title": "Probe command passed",
                "type": "command",
                "required": True,
                "command": "printf 'hello'",
                "evidence_refs": ["probe-log"],
            }
        ],
        "observability": {"events": ["flow.started", "node.completed", "gate.completed", "flow.completed"]},
    }


def test_run_flow_executes_command_and_emits_valid_bundle(tmp_path: Path) -> None:
    document = _minimal_runnable_flow()
    flow_schema = load_json(DEFAULT_SCHEMA)
    assert validate_flow_document(document, flow_schema) == []

    flow_file = tmp_path / "flow.yaml"
    flow_file.write_text(dump_yaml(document), encoding="utf-8")

    out_dir = tmp_path / "out"
    bundle, status, needs_handler = run_flow(
        document,
        flow_source="../flow.yaml",
        inputs={"repo": "."},
        params={},
        workdir=tmp_path,
        out_dir=out_dir,
    )

    assert status == "completed"
    assert needs_handler == []
    assert bundle["run"]["status"] == "completed"
    assert "result" in bundle["outputs"]
    gate_ids = [e["payload"]["gate_id"] for e in bundle["events"] if e["event"] == "gate.completed"]
    assert "probe-passed" in gate_ids
    assert any(e["event"] == "flow.completed" for e in bundle["events"])

    log_artifact = next(a for a in bundle["artifacts"] if a["id"] == "probe-log")
    log_text = (out_dir / log_artifact["uri"]).read_text(encoding="utf-8")
    assert "hello from runner" in log_text

    run_schema = load_json(Path("schemas/run.schema.json"))
    event_schema = load_json(Path("schemas/event.schema.json"))
    errors = validate_run_document(
        bundle, run_schema, event_schema, flow_schema, run_path=out_dir / "run.json"
    )
    assert errors == []


def test_run_flow_failed_command_marks_run_failed(tmp_path: Path) -> None:
    document = _minimal_runnable_flow()
    document["nodes"][1]["command"] = "false"

    bundle, status, _ = run_flow(
        document,
        flow_source="flows/test/runner-smoke/flow.yaml",
        inputs={"repo": "."},
        params={},
        workdir=tmp_path,
        out_dir=tmp_path / "out",
    )

    assert status == "failed"
    assert bundle["run"]["status"] == "failed"
    assert not any(e["event"] == "flow.completed" for e in bundle["events"])


def test_run_flow_agent_task_without_command_needs_handler(tmp_path: Path) -> None:
    document = _minimal_runnable_flow()
    document["nodes"].insert(
        2,
        {
            "id": "author",
            "type": "agent_task",
            "title": "Author the result",
            "description": "Needs a consumer-supplied agent to produce the result.",
            "agent": "worker",
            "requires": ["probe-log"],
            "produces": ["draft"],
        },
    )

    bundle, status, needs_handler = run_flow(
        document,
        flow_source="flows/test/runner-smoke/flow.yaml",
        inputs={"repo": "."},
        params={},
        workdir=tmp_path,
        out_dir=tmp_path / "out",
    )

    assert "author" in needs_handler
    assert status == "incomplete"
    assert bundle["run"]["status"] == "failed"


def test_run_flow_consumer_handler_binds_agent_task(tmp_path: Path) -> None:
    document = _minimal_runnable_flow()
    document["nodes"].insert(
        2,
        {
            "id": "author",
            "type": "agent_task",
            "title": "Author the result",
            "description": "A consumer supplies the agent that produces this node's output.",
            "agent": "worker",
            "requires": ["probe-log"],
            "produces": ["draft"],
        },
    )

    bundle, status, needs_handler = run_flow(
        document,
        flow_source="flows/test/runner-smoke/flow.yaml",
        inputs={"repo": "."},
        params={},
        workdir=tmp_path,
        out_dir=tmp_path / "out",
        handlers={"author": "printf 'drafted by the consumer agent'"},
    )

    assert needs_handler == []
    assert status == "completed"
    assert bundle["run"]["status"] == "completed"
    draft = next(a for a in bundle["artifacts"] if a["id"] == "draft")
    assert (tmp_path / "out" / draft["uri"]).read_text(encoding="utf-8").endswith("consumer agent")
    author_event = next(
        e for e in bundle["events"] if e["event"] == "node.completed" and e.get("node_id") == "author"
    )
    assert author_event["payload"].get("handler") == "consumer"
