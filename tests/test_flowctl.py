from pathlib import Path

import json

from flowctl import composition
from flowctl.cli import (
    DEFAULT_ADAPTER_SMOKE_SCHEMA,
    DEFAULT_EVENT_SCHEMA,
    DEFAULT_EVENT_STREAM_SCHEMA,
    DEFAULT_RUN_SCHEMA,
    DEFAULT_SAMPLE_SCHEMA,
    DEFAULT_SCHEMA,
    build_flow_catalog,
    build_replay_summary,
    build_report_summary,
    collect_release_package_files,
    dump_yaml,
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


def test_semver_constraint_resolution() -> None:
    constraint = composition.parse_constraint(">=0.1.0 <0.2.0")
    assert constraint is not None
    assert composition.version_satisfies("0.1.5", constraint)
    assert not composition.version_satisfies("0.2.0", constraint)
    assert composition.resolve_version(constraint, ["0.1.0", "0.1.5", "0.2.0"]) == "0.1.5"
    assert composition.parse_constraint("not-a-range") is None


def test_webapp_program_composition_is_valid() -> None:
    catalog, _ = build_flow_catalog([])
    program = load_yaml(Path("flows/program/webapp-build/flow.yaml"))
    assert composition.validate_composition_static(program, catalog) == []


def test_webapp_program_run_validates_child_subruns() -> None:
    run_schema = load_json(DEFAULT_RUN_SCHEMA)
    event_schema = load_json(DEFAULT_EVENT_SCHEMA)
    flow_schema = load_json(DEFAULT_SCHEMA)
    path = Path("examples/runs/webapp-build.run.json")
    errors = validate_run_document(load_json(path), run_schema, event_schema, flow_schema, run_path=path)
    assert errors == []


def test_run_without_subruns_is_rejected() -> None:
    run_schema = load_json(DEFAULT_RUN_SCHEMA)
    event_schema = load_json(DEFAULT_EVENT_SCHEMA)
    flow_schema = load_json(DEFAULT_SCHEMA)
    path = Path("tests/fixtures/invalid-run-subflow-missing.json")
    errors = validate_run_document(load_json(path), run_schema, event_schema, flow_schema, run_path=path)
    assert any("no sub_run for flow_ref node" in error for error in errors)


def test_composition_static_rejects_expose_mismatch() -> None:
    catalog, _ = build_flow_catalog([])
    program = load_yaml(Path("flows/program/webapp-build/flow.yaml"))
    for node in program["nodes"]:
        if node.get("id") == "backend":
            node["produces"] = ["wrong-name"]
    errors = composition.validate_composition_static(program, catalog)
    assert any("must equal the exposed artifact names" in error for error in errors)


def test_composition_static_rejects_unresolvable_ref() -> None:
    catalog, _ = build_flow_catalog([])
    program = load_yaml(Path("flows/program/webapp-build/flow.yaml"))
    for node in program["nodes"]:
        if node.get("id") == "design":
            node["ref"] = {"flow_id": "design.does-not-exist", "version_constraint": ">=0.1.0"}
    errors = composition.validate_composition_static(program, catalog)
    assert any("nonexistent flow_id" in error for error in errors)


def test_evidence_class_mismatch_is_rejected() -> None:
    rs = load_json(DEFAULT_RUN_SCHEMA)
    es = load_json(DEFAULT_EVENT_SCHEMA)
    fs = load_json(DEFAULT_SCHEMA)
    path = Path("tests/fixtures/invalid-run-evidence-class-mismatch.json")
    errors = validate_run_document(load_json(path), rs, es, fs, run_path=path)
    assert any("requires evidence_class" in error for error in errors)


def test_standalone_forbidden_evidence_class_is_rejected() -> None:
    rs = load_json(DEFAULT_RUN_SCHEMA)
    es = load_json(DEFAULT_EVENT_SCHEMA)
    fs = load_json(DEFAULT_SCHEMA)
    path = Path("tests/fixtures/invalid-run-standalone-sandbox.json")
    errors = validate_run_document(load_json(path), rs, es, fs, run_path=path)
    assert any("standalone runs may not emit" in error for error in errors)


def test_evidence_class_ordering() -> None:
    from flowctl.cli import evidence_class_satisfies

    assert evidence_class_satisfies({"judgment"}, "judgment", None)
    assert not evidence_class_satisfies({"deterministic"}, "judgment", None)
    assert evidence_class_satisfies({"sandbox-run"}, None, "fixture")
    assert not evidence_class_satisfies({"deterministic"}, None, "sandbox-run")


def test_undeclared_parameter_reference_is_rejected() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    invalid = load_yaml(Path("tests/fixtures/invalid-parameter-reference.yaml"))
    errors = validate_flow_document(invalid, schema)
    assert any("references undeclared parameter 'missing'" in error for error in errors)


def test_backend_service_parameterizes_stack_commands() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    document = load_yaml(Path("flows/engineering/backend-service/flow.yaml"))
    declared = {param["id"] for param in document.get("parameters", [])}
    assert {"build_command", "test_command"} <= declared
    assert validate_flow_document(document, schema) == []


def test_self_review_is_rejected() -> None:
    rs = load_json(DEFAULT_RUN_SCHEMA)
    es = load_json(DEFAULT_EVENT_SCHEMA)
    fs = load_json(DEFAULT_SCHEMA)
    path = Path("tests/fixtures/invalid-run-self-review.json")
    errors = validate_run_document(load_json(path), rs, es, fs, run_path=path)
    assert any("must not be a producing agent" in error for error in errors)


def test_missing_reviewer_on_judgment_gate_is_rejected() -> None:
    rs = load_json(DEFAULT_RUN_SCHEMA)
    es = load_json(DEFAULT_EVENT_SCHEMA)
    fs = load_json(DEFAULT_SCHEMA)
    path = Path("tests/fixtures/invalid-run-missing-reviewer.json")
    errors = validate_run_document(load_json(path), rs, es, fs, run_path=path)
    assert any("requires a reviewer_id" in error for error in errors)


def test_unbounded_iteration_is_rejected() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    invalid = load_yaml(Path("tests/fixtures/invalid-iteration-unbounded.yaml"))
    errors = validate_flow_document(invalid, schema)
    assert any("require an integer max_iterations" in error for error in errors)


def test_fanout_missing_cardinality_is_rejected() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    invalid = load_yaml(Path("tests/fixtures/invalid-fanout-missing-cardinality.yaml"))
    errors = validate_flow_document(invalid, schema)
    assert any("requires a cardinality" in error for error in errors)


def test_shipped_iteration_and_fanout_validate() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    frontend = load_yaml(Path("flows/engineering/frontend-build/flow.yaml"))
    backend = load_yaml(Path("flows/engineering/backend-service/flow.yaml"))
    assert validate_flow_document(frontend, schema) == []
    assert validate_flow_document(backend, schema) == []
    assert any(node.get("iteration") for node in frontend["nodes"])
    assert any(node.get("fan_out") for node in backend["nodes"])


def test_backend_nilcore_sandbox_run_validates() -> None:
    rs = load_json(DEFAULT_RUN_SCHEMA)
    es = load_json(DEFAULT_EVENT_SCHEMA)
    fs = load_json(DEFAULT_SCHEMA)
    path = Path("examples/runs/webapp/backend-nilcore.run.json")
    errors = validate_run_document(load_json(path), rs, es, fs, run_path=path)
    assert errors == []


def test_sandbox_evidence_requires_provenance() -> None:
    rs = load_json(DEFAULT_RUN_SCHEMA)
    es = load_json(DEFAULT_EVENT_SCHEMA)
    fs = load_json(DEFAULT_SCHEMA)
    path = Path("tests/fixtures/invalid-run-sandbox-no-provenance.json")
    errors = validate_run_document(load_json(path), rs, es, fs, run_path=path)
    assert any("requires an env.provisioned" in error for error in errors)


def test_self_provisioned_environment_is_rejected() -> None:
    rs = load_json(DEFAULT_RUN_SCHEMA)
    es = load_json(DEFAULT_EVENT_SCHEMA)
    fs = load_json(DEFAULT_SCHEMA)
    path = Path("tests/fixtures/invalid-run-self-provisioned.json")
    errors = validate_run_document(load_json(path), rs, es, fs, run_path=path)
    assert any("must be a runtime" in error for error in errors)


def test_missing_teardown_is_rejected() -> None:
    rs = load_json(DEFAULT_RUN_SCHEMA)
    es = load_json(DEFAULT_EVENT_SCHEMA)
    fs = load_json(DEFAULT_SCHEMA)
    path = Path("tests/fixtures/invalid-run-missing-teardown.json")
    errors = validate_run_document(load_json(path), rs, es, fs, run_path=path)
    assert any("requires a matching env.torn_down" in error for error in errors)


def test_duplicate_subrun_is_rejected() -> None:
    rs = load_json(DEFAULT_RUN_SCHEMA)
    es = load_json(DEFAULT_EVENT_SCHEMA)
    fs = load_json(DEFAULT_SCHEMA)
    path = Path("tests/fixtures/invalid-run-duplicate-subrun.json")
    errors = validate_run_document(load_json(path), rs, es, fs, run_path=path)
    assert any("duplicate sub_run" in error for error in errors)


def test_composition_detects_cycles() -> None:
    assert composition.find_cycle("a", {"a": {"b"}, "b": {"c"}, "c": {"a"}}) is not None
    assert composition.find_cycle("a", {"a": {"b"}, "b": set()}) is None


def test_build_flow_catalog_indexes_flows() -> None:
    catalog, _ = build_flow_catalog([])
    assert "program.webapp-build" in catalog
    assert any(entry["version"] == "0.1.0" for entry in catalog["engineering.backend-service"])


def test_check_composition_cli_passes() -> None:
    from flowctl.cli import main

    assert main(["check-composition"]) == 0
