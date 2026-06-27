from pathlib import Path

import json

from flowctl.cli import (
    DEFAULT_SCHEMA,
    build_replay_summary,
    build_report_summary,
    find_flow_files,
    find_json_files,
    find_markdown_files,
    find_run_files,
    find_sample_files,
    load_json,
    load_yaml,
    validate_event_document,
    validate_flow_document,
    validate_changelog,
    validate_markdown_links,
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
    assert Path("examples/samples/coding/feature-implementation.sample.json").resolve() not in paths


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
