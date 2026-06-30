from pathlib import Path

import json
import re

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
    plan_flow,
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


def test_wave1_flows_validate() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    for path in (
        "flows/ops/ephemeral-preview-deploy/flow.yaml",
        "flows/ops/integration-test-lab/flow.yaml",
        "flows/engineering/browser-matrix-check/flow.yaml",
    ):
        assert validate_flow_document(load_yaml(Path(path)), schema) == [], path


def test_wave1_sandbox_runs_validate() -> None:
    rs = load_json(DEFAULT_RUN_SCHEMA)
    es = load_json(DEFAULT_EVENT_SCHEMA)
    fs = load_json(DEFAULT_SCHEMA)
    for path in (
        "examples/runs/ephemeral-preview-deploy.run.json",
        "examples/runs/integration-test-lab.run.json",
        "examples/runs/browser-matrix-check.run.json",
    ):
        assert validate_run_document(load_json(Path(path)), rs, es, fs, run_path=Path(path)) == [], path


def test_preview_deploy_uses_probe_gate() -> None:
    doc = load_yaml(Path("flows/ops/ephemeral-preview-deploy/flow.yaml"))
    assert any(gate["type"] == "probe" for gate in doc["quality_gates"])


def test_wave2_flows_validate() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    for path in (
        "flows/design/service-to-spec/flow.yaml",
        "flows/engineering/cli-tool/flow.yaml",
        "flows/engineering/library-package/flow.yaml",
        "flows/infra/iac-module/flow.yaml",
    ):
        assert validate_flow_document(load_yaml(Path(path)), schema) == [], path


def test_wave2_runs_validate() -> None:
    rs = load_json(DEFAULT_RUN_SCHEMA)
    es = load_json(DEFAULT_EVENT_SCHEMA)
    fs = load_json(DEFAULT_SCHEMA)
    for path in (
        "examples/runs/service-to-spec.run.json",
        "examples/runs/cli-tool.run.json",
        "examples/runs/library-package.run.json",
        "examples/runs/iac-module.run.json",
    ):
        assert validate_run_document(load_json(Path(path)), rs, es, fs, run_path=Path(path)) == [], path


def test_service_to_spec_output_feeds_backend_service() -> None:
    spec = load_yaml(Path("flows/design/service-to-spec/flow.yaml"))
    backend = load_yaml(Path("flows/engineering/backend-service/flow.yaml"))
    spec_outputs = {field["id"] for field in spec["contracts"]["outputs"]}
    backend_inputs = {field["id"] for field in backend["contracts"]["inputs"]}
    # the design spec is the shape the backend build consumes (program.service-from-spec composition)
    assert "design_spec" in spec_outputs
    assert "target_spec" in backend_inputs


def test_cli_tool_uses_bounded_iteration() -> None:
    doc = load_yaml(Path("flows/engineering/cli-tool/flow.yaml"))
    assert any(
        isinstance(node.get("iteration"), dict) and isinstance(node["iteration"].get("max_iterations"), int)
        for node in doc["nodes"]
    )


def test_wave3_programs_validate_and_compose() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    catalog, _ = build_flow_catalog([])
    for path in (
        "flows/program/service-from-spec/flow.yaml",
        "flows/program/feature-to-release/flow.yaml",
        "flows/program/security-hardening-campaign/flow.yaml",
    ):
        doc = load_yaml(Path(path))
        assert validate_flow_document(doc, schema) == [], path
        assert composition.validate_composition_static(doc, catalog) == [], path


def test_wave3_program_runs_validate_recursively() -> None:
    rs = load_json(DEFAULT_RUN_SCHEMA)
    es = load_json(DEFAULT_EVENT_SCHEMA)
    fs = load_json(DEFAULT_SCHEMA)
    for path in (
        "examples/runs/service-from-spec.run.json",
        "examples/runs/feature-to-release.run.json",
        "examples/runs/security-hardening-campaign.run.json",
    ):
        assert validate_run_document(load_json(Path(path)), rs, es, fs, run_path=Path(path)) == [], path


def test_security_campaign_combines_fanout_iteration_flowref() -> None:
    doc = load_yaml(Path("flows/program/security-hardening-campaign/flow.yaml"))
    types = [node.get("type") for node in doc["nodes"]]
    assert types.count("flow_ref") >= 2
    harden = next(node for node in doc["nodes"] if node["id"] == "harden")
    assert isinstance(harden.get("fan_out"), dict)
    assert isinstance(harden.get("iteration"), dict)


def test_inplace_v1_1_primitive_upgrades() -> None:
    flaky = load_yaml(Path("flows/engineering/flaky-test-stabilization/flow.yaml"))
    perf = load_yaml(Path("flows/engineering/performance-regression/flow.yaml"))
    swarm = load_yaml(Path("flows/orchestration/swarm-execution/flow.yaml"))
    assert flaky["spec_version"] == "agentic-flows/v1.1"
    assert any(isinstance(node.get("iteration"), dict) for node in flaky["nodes"])
    assert any(isinstance(node.get("iteration"), dict) for node in perf["nodes"])
    assert any(isinstance(node.get("fan_out"), dict) for node in swarm["nodes"])
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


def test_plan_flow_reports_consumption_surface_and_honors_handlers() -> None:
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

    plan = plan_flow(document)
    by_id = {step["id"]: step["disposition"] for step in plan["steps"]}
    assert by_id["intake"] == "data"
    assert by_id["probe"] == "command"
    assert by_id["author"] == "needs-handler"
    assert plan["needs_handlers"] == ["author"]

    bound = plan_flow(document, {"author": "printf hi"})
    assert bound["needs_handlers"] == []
    assert {s["id"]: s["disposition"] for s in bound["steps"]}["author"] == "handler"


def test_simulate_completes_flow_without_running_commands(tmp_path: Path) -> None:
    document = _minimal_runnable_flow()
    # A command that would fail if actually executed - simulate must not run it.
    document["nodes"][1]["command"] = "exit 7"
    document["nodes"].insert(
        2,
        {
            "id": "author",
            "type": "agent_task",
            "title": "Author the result",
            "description": "An agent step a consumer would supply; simulated here.",
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
        simulate=True,
    )

    assert status == "completed"
    assert needs_handler == []
    probe_event = next(
        e for e in bundle["events"] if e["event"] == "node.completed" and e.get("node_id") == "probe"
    )
    assert probe_event["payload"].get("simulated") is True


def test_every_flow_is_structurally_completable(tmp_path: Path) -> None:
    # With every working/agent step assumed to succeed, each catalog flow must
    # reach status completed: required gates satisfiable, required outputs produced.
    failures: list[str] = []
    for flow_path in find_flow_files([Path("flows")]):
        document = load_yaml(flow_path)
        out_dir = tmp_path / re.sub(r"[^a-z0-9]+", "-", document["id"])
        _, status, _ = run_flow(
            document,
            flow_source=str(flow_path),
            inputs={},
            params={},
            workdir=tmp_path,
            out_dir=out_dir,
            simulate=True,
        )
        if status != "completed":
            failures.append(f"{flow_path}: {status}")
    assert not failures, "\n".join(failures)


def test_every_flow_has_a_well_defined_consumption_surface() -> None:
    # A node is a data step (the runner assembles it), a command step, or a node a
    # consumer must bind. The invariant: every node is classified, and every
    # needs-handler node is genuinely a non-data, command-less node.
    allowed = {"command", "data", "handler", "needs-handler"}
    data_types = {"intake", "plan", "decision", "verifier", "finalizer"}
    failures: list[str] = []

    for flow_path in find_flow_files([Path("flows")]):
        document = load_yaml(flow_path)
        node_ids = [node["id"] for node in document["nodes"]]
        nodes_by_id = {node["id"]: node for node in document["nodes"]}
        plan = plan_flow(document)

        planned_ids = [step["id"] for step in plan["steps"]]
        if sorted(planned_ids) != sorted(node_ids):
            failures.append(f"{flow_path}: plan {sorted(planned_ids)} != nodes {sorted(node_ids)}")
        for step in plan["steps"]:
            if step["disposition"] not in allowed:
                failures.append(f"{flow_path}: {step['id']} has bad disposition {step['disposition']}")
        for node_id in plan["needs_handlers"]:
            node = nodes_by_id[node_id]
            if node["type"] in data_types or node.get("command"):
                failures.append(f"{flow_path}: {node_id} wrongly marked needs-handler")

    assert not failures, "\n".join(failures)


def test_external_production_flows_ship_no_fabricated_run_bundle() -> None:
    # Honesty invariant: a flow with an `external-production` gate is contract-first —
    # a completed standalone/local run would fabricate the external state, so none ships.
    offenders: list[str] = []
    for flow_path in find_flow_files([Path("flows")]):
        document = load_yaml(flow_path)
        has_external = any(
            gate.get("evidence_class") == "external-production" for gate in document.get("quality_gates", [])
        )
        if not has_external:
            continue
        run_path = Path("examples/runs") / f"{flow_path.parent.name}.run.json"
        if run_path.exists():
            run = load_json(run_path)
            if run.get("run", {}).get("status") == "completed":
                offenders.append(str(run_path))
    assert offenders == [], offenders


def test_deferred_backlog_flows_are_contract_first() -> None:
    # Every shipped contract-first deferred flow validates, has a sample, a judgment
    # decision gate with reviewer-identity, and no completed run bundle.
    schema = load_json(DEFAULT_SCHEMA)
    deferred = [
        "personal/daily-command-center", "personal/inbox-triage-and-reply", "personal/cross-channel-briefing",
        "engineering/merge-readiness", "engineering/release-train", "security/secret-leak-response",
        "research/competitor-watch", "ops/cost-anomaly", "ops/rollback", "ops/infrastructure-drift",
        "ops/backup-restore-drill", "ops/scheduler-health", "product/kpi-diagnostics", "product/churn-risk-review",
        "product/customer-success-brief", "product/experiment-readout", "product/pricing-or-packaging-analysis",
        "product/release-positioning", "docs/public-announcement",
    ]
    for rel in deferred:
        document = load_yaml(Path(f"flows/{rel}/flow.yaml"))
        assert validate_flow_document(document, schema) == [], rel
        assert any(gate["type"] == "judgment" for gate in document["quality_gates"]), rel
        assert not (Path("examples/runs") / f"{Path(rel).name}.run.json").exists(), rel
