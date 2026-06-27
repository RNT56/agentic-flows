from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by users without deps
    raise SystemExit("PyYAML is required. Install with: python -m pip install -e .") from exc

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover - exercised by users without deps
    raise SystemExit("jsonschema is required. Install with: python -m pip install -e .") from exc


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCHEMA = REPO_ROOT / "schemas" / "flow.schema.json"
DEFAULT_SEARCH_ROOTS = [REPO_ROOT / "flows", REPO_ROOT / "templates"]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: expected a YAML mapping at document root")
    return loaded


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: expected a JSON object at document root")
    return loaded


def find_flow_files(paths: Iterable[Path]) -> list[Path]:
    selected = list(paths)
    if not selected:
        selected = DEFAULT_SEARCH_ROOTS

    files: list[Path] = []
    for path in selected:
        path = path.resolve()
        if path.is_file():
            files.append(path)
            continue
        if not path.exists():
            files.append(path)
            continue
        files.extend(sorted(path.rglob("flow.yaml")))
        files.extend(sorted(path.rglob("flow.yml")))

    return sorted(dict.fromkeys(files))


def format_error_path(parts: Iterable[Any]) -> str:
    path = "$"
    for part in parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def validate_flow_document(document: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = [
        f"{format_error_path(error.path)}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    ]
    errors.extend(validate_semantics(document))
    return errors


def validate_semantics(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    nodes = document.get("nodes", [])
    if not isinstance(nodes, list):
        return errors

    node_ids: list[str] = []
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if isinstance(node_id, str):
            node_ids.append(node_id)
        else:
            errors.append(f"$.nodes[{index}].id: expected string id")

    duplicate_ids = sorted({node_id for node_id in node_ids if node_ids.count(node_id) > 1})
    for node_id in duplicate_ids:
        errors.append(f"$.nodes: duplicate node id '{node_id}'")

    node_id_set = set(node_ids)
    entrypoint = document.get("entrypoint")
    if isinstance(entrypoint, str) and entrypoint not in node_id_set:
        errors.append(f"$.entrypoint: references missing node '{entrypoint}'")

    adjacency: dict[str, list[str]] = {node_id: [] for node_id in node_id_set}
    for index, edge in enumerate(document.get("edges", [])):
        if not isinstance(edge, dict):
            continue
        start = edge.get("from")
        end = edge.get("to")
        if isinstance(start, str) and start not in node_id_set:
            errors.append(f"$.edges[{index}].from: references missing node '{start}'")
        if isinstance(end, str) and end not in node_id_set:
            errors.append(f"$.edges[{index}].to: references missing node '{end}'")
        if isinstance(start, str) and isinstance(end, str) and start in node_id_set and end in node_id_set:
            adjacency[start].append(end)

    if isinstance(entrypoint, str) and entrypoint in node_id_set:
        reachable = collect_reachable(entrypoint, adjacency)
        unreachable = sorted(node_id_set - reachable)
        for node_id in unreachable:
            errors.append(f"$.nodes: node '{node_id}' is not reachable from entrypoint '{entrypoint}'")

    gates = document.get("quality_gates", [])
    if isinstance(gates, list):
        required_gate_count = sum(1 for gate in gates if isinstance(gate, dict) and gate.get("required") is True)
        if required_gate_count == 0:
            errors.append("$.quality_gates: at least one gate must be required")
        for index, gate in enumerate(gates):
            if not isinstance(gate, dict):
                continue
            if gate.get("type") == "command" and not gate.get("command"):
                errors.append(f"$.quality_gates[{index}].command: command gates require a command")

    return errors


def collect_reachable(entrypoint: str, adjacency: dict[str, list[str]]) -> set[str]:
    seen: set[str] = set()
    stack = [entrypoint]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(adjacency.get(current, []))
    return seen


def cmd_validate(args: argparse.Namespace) -> int:
    schema = load_json(args.schema)
    flow_files = find_flow_files(args.paths)
    if not flow_files:
        print("No flow.yaml files found", file=sys.stderr)
        return 1

    failures = 0
    for path in flow_files:
        if not path.exists():
            print(f"FAIL {path}: path does not exist", file=sys.stderr)
            failures += 1
            continue
        try:
            document = load_yaml(path)
            errors = validate_flow_document(document, schema)
        except Exception as exc:  # noqa: BLE001 - CLI should report file context
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            failures += 1
            continue

        if errors:
            failures += 1
            print(f"FAIL {path}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        elif args.verbose:
            print(f"OK   {path}")

    if failures:
        print(f"{failures} flow file(s) failed validation", file=sys.stderr)
        return 1

    print(f"Validated {len(flow_files)} flow file(s)")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    schema = load_json(args.schema)
    rows: list[tuple[str, str, str, str]] = []
    failures = 0
    for path in find_flow_files(args.paths):
        try:
            document = load_yaml(path)
            errors = validate_flow_document(document, schema)
        except Exception as exc:  # noqa: BLE001 - CLI should report file context
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            failures += 1
            continue
        if errors:
            print(f"FAIL {path}: invalid flow", file=sys.stderr)
            failures += 1
            continue
        runtime = document.get("runtime", {})
        supported = ", ".join(runtime.get("supported_cores", []))
        rows.append((document["id"], document["version"], document["stability"], supported))

    if failures:
        return 1

    if args.json:
        print(json.dumps([{"id": row[0], "version": row[1], "stability": row[2], "supported_cores": row[3].split(", ")} for row in rows], indent=2))
        return 0

    print(f"{'ID':42} {'VERSION':10} {'STABILITY':12} CORES")
    print("-" * 90)
    for row in rows:
        print(f"{row[0]:42} {row[1]:10} {row[2]:12} {row[3]}")
    return 0


def cmd_graph(args: argparse.Namespace) -> int:
    schema = load_json(args.schema)
    document = load_yaml(args.flow)
    errors = validate_flow_document(document, schema)
    if errors:
        print(f"FAIL {args.flow}", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    output = graph_as_dot(document) if args.format == "dot" else json.dumps(graph_as_json(document), indent=2)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


def graph_as_json(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": document["id"],
        "version": document["version"],
        "entrypoint": document["entrypoint"],
        "nodes": [
            {
                "id": node["id"],
                "type": node["type"],
                "title": node["title"],
            }
            for node in document["nodes"]
        ],
        "edges": document["edges"],
    }


def graph_as_dot(document: dict[str, Any]) -> str:
    lines = [f'digraph "{escape_dot(document["id"])}" {{', "  rankdir=LR;"]
    for node in document["nodes"]:
        label = f'{node["title"]}\\n{node["type"]}'
        lines.append(f'  "{escape_dot(node["id"])}" [label="{escape_dot(label)}"];')
    for edge in document["edges"]:
        label = edge.get("condition")
        if label:
            lines.append(f'  "{escape_dot(edge["from"])}" -> "{escape_dot(edge["to"])}" [label="{escape_dot(label)}"];')
        else:
            lines.append(f'  "{escape_dot(edge["from"])}" -> "{escape_dot(edge["to"])}";')
    lines.append("}")
    return "\n".join(lines)


def escape_dot(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="flowctl", description="Validate and inspect agentic flow definitions.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="Path to the flow JSON Schema.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate flow.yaml files.")
    validate.add_argument("paths", nargs="*", type=Path, help="Flow files or directories. Defaults to flows/ and templates/.")
    validate.add_argument("-v", "--verbose", action="store_true", help="Print each passing file.")
    validate.set_defaults(func=cmd_validate)

    list_cmd = subparsers.add_parser("list", help="List valid flow definitions.")
    list_cmd.add_argument("paths", nargs="*", type=Path, help="Flow files or directories. Defaults to flows/ and templates/.")
    list_cmd.add_argument("--json", action="store_true", help="Print JSON output.")
    list_cmd.set_defaults(func=cmd_list)

    graph = subparsers.add_parser("graph", help="Export a flow graph.")
    graph.add_argument("flow", type=Path, help="Path to flow.yaml.")
    graph.add_argument("--format", choices=("json", "dot"), default="json")
    graph.add_argument("--output", type=Path, help="Write output to a file.")
    graph.set_defaults(func=cmd_graph)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

