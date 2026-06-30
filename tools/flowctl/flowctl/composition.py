"""Sub-flow composition support for agentic-flows v1.1.

Pure, dependency-free helpers for resolving ``flow_ref`` nodes:

- a small semver-range parser (``parse_constraint`` / ``version_satisfies`` / ``resolve_version``),
- a flow-catalog index keyed by flow id,
- the static ``check-composition`` rules.

The run-time arm (recursive child-bundle validation) lives in ``cli.py`` because it
depends on run-bundle loading and ``validate_run_document``.
"""

from __future__ import annotations

import re
from typing import Any

_SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
_COMPARATOR = re.compile(r"^(>=|<=|>|<|=)?(\d+)\.(\d+)\.(\d+)$")

Version = tuple[int, int, int]
Comparator = tuple[str, Version]


def parse_version(text: Any) -> Version | None:
    match = _SEMVER.match(text) if isinstance(text, str) else None
    return (int(match[1]), int(match[2]), int(match[3])) if match else None


def parse_constraint(text: Any) -> list[Comparator] | None:
    """Parse a whitespace-separated semver range like ``>=0.1.0 <0.2.0``.

    Returns ``None`` when the constraint cannot be parsed, so callers can fail
    closed rather than silently mis-evaluate.
    """
    if not isinstance(text, str) or not text.strip():
        return None
    comparators: list[Comparator] = []
    for token in text.split():
        match = _COMPARATOR.match(token)
        if not match:
            return None
        op = match[1] or "="
        comparators.append((op, (int(match[2]), int(match[3]), int(match[4]))))
    return comparators or None


def version_satisfies(version: Any, constraint: list[Comparator]) -> bool:
    parsed = parse_version(version)
    if parsed is None:
        return False
    for op, target in constraint:
        if op == ">=" and not parsed >= target:
            return False
        if op == ">" and not parsed > target:
            return False
        if op == "<=" and not parsed <= target:
            return False
        if op == "<" and not parsed < target:
            return False
        if op == "=" and not parsed == target:
            return False
    return True


def resolve_version(constraint: list[Comparator], available: list[str]) -> str | None:
    """Return the highest available version satisfying the constraint, or ``None``."""
    candidates = [version for version in available if version_satisfies(version, constraint)]
    if not candidates:
        return None
    return max(candidates, key=lambda value: parse_version(value) or (0, 0, 0))


def contract_ids(document: dict[str, Any], section: str) -> set[str]:
    return {
        field["id"]
        for field in document.get("contracts", {}).get(section, [])
        if isinstance(field, dict) and isinstance(field.get("id"), str)
    }


def required_input_ids(document: dict[str, Any]) -> set[str]:
    return {
        field["id"]
        for field in document.get("contracts", {}).get("inputs", [])
        if isinstance(field, dict) and isinstance(field.get("id"), str) and field.get("required") is True
    }


def flow_ref_nodes(document: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        node
        for node in document.get("nodes", [])
        if isinstance(node, dict) and node.get("type") == "flow_ref"
    ]


def resolve_child(node: dict[str, Any], catalog: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, Any] | None, str | None, str | None]:
    """Resolve a flow_ref node against the catalog.

    Returns ``(child_document, resolved_version, error)``. Exactly one of the
    first pair and ``error`` is meaningful.
    """
    ref = node.get("ref") or {}
    flow_id = ref.get("flow_id")
    constraint_text = ref.get("version_constraint")
    entries = catalog.get(flow_id)
    if not entries:
        return None, None, f"ref to nonexistent flow_id '{flow_id}'"
    constraint = parse_constraint(constraint_text)
    if constraint is None:
        return None, None, f"unparseable version_constraint '{constraint_text}'"
    resolved = resolve_version(constraint, [entry["version"] for entry in entries])
    if resolved is None:
        return None, None, f"no catalog version of '{flow_id}' satisfies '{constraint_text}'"
    child = next(entry["document"] for entry in entries if entry["version"] == resolved)
    return child, resolved, None


def build_ref_graph(catalog: dict[str, list[dict[str, Any]]]) -> dict[str, set[str]]:
    """flow_id -> set(child flow_id) over the whole catalog (highest resolved version)."""
    graph: dict[str, set[str]] = {}
    for flow_id, entries in catalog.items():
        children: set[str] = set()
        for entry in entries:
            for node in flow_ref_nodes(entry["document"]):
                child, _, error = resolve_child(node, catalog)
                if child is not None and isinstance(child.get("id"), str):
                    children.add(child["id"])
        graph[flow_id] = children
    return graph


def find_cycle(start: str, graph: dict[str, set[str]]) -> list[str] | None:
    """Return a cycle path through ``start`` if one exists, else ``None``.

    Uses three-colour DFS: ``on_path`` (gray) is the current stack, ``finished`` (black)
    memoises nodes already proven cycle-free so a node reachable by many paths in a diamond
    graph is explored once, not once per path. Without this the walk is exponential.
    """
    path: list[str] = []
    on_path: set[str] = set()
    finished: set[str] = set()

    def dfs(node: str) -> list[str] | None:
        if node in on_path:
            return path[path.index(node):] + [node]
        if node in finished:
            return None
        on_path.add(node)
        path.append(node)
        for child in graph.get(node, set()):
            cycle = dfs(child)
            if cycle:
                return cycle
        path.pop()
        on_path.discard(node)
        finished.add(node)
        return None

    return dfs(start)


def validate_composition_static(document: dict[str, Any], catalog: dict[str, list[dict[str, Any]]]) -> list[str]:
    """Static composition checks for one flow document against a catalog."""
    errors: list[str] = []
    nodes = document.get("nodes", [])
    parent_caps = set(document.get("runtime", {}).get("required_capabilities", []))
    parent_cores = set(document.get("runtime", {}).get("supported_cores", []))

    for index, node in enumerate(nodes):
        if not isinstance(node, dict) or node.get("type") != "flow_ref":
            continue
        node_ref = f"$.nodes[{index}]({node.get('id')})"
        child, resolved, error = resolve_child(node, catalog)
        if error:
            errors.append(f"{node_ref}.ref: {error}")
            continue

        child_inputs = contract_ids(child, "inputs")
        child_outputs = contract_ids(child, "outputs")
        child_required = required_input_ids(child)
        with_keys = set(node.get("with", {}) or {})
        expose = node.get("expose", {}) or {}

        for key in sorted(with_keys - child_inputs):
            errors.append(f"{node_ref}.with: '{key}' is not a declared input of '{child['id']}'")
        for key in sorted(child_required - with_keys):
            errors.append(f"{node_ref}.with: required child input '{key}' is not bound")
        for key in sorted(set(expose) - child_outputs):
            errors.append(f"{node_ref}.expose: '{key}' is not a declared output of '{child['id']}'")
        if set(node.get("produces", []) or []) != set(expose.values()):
            errors.append(f"{node_ref}.produces: must equal the exposed artifact names {sorted(set(expose.values()))}")

        child_caps = set(child.get("runtime", {}).get("required_capabilities", []))
        missing_caps = sorted(child_caps - parent_caps)
        if missing_caps:
            errors.append(
                f"{node_ref}: parent must require capabilities used by child '{child['id']}': missing {missing_caps}"
            )
        child_cores = set(child.get("runtime", {}).get("supported_cores", []))
        if not parent_cores <= child_cores:
            unsupported = sorted(parent_cores - child_cores)
            errors.append(
                f"{node_ref}: parent supported_cores must be a subset of child '{child['id']}' cores; "
                f"unsupported by child: {unsupported}"
            )

    flow_id = document.get("id")
    if isinstance(flow_id, str) and flow_ref_nodes(document):
        graph = build_ref_graph(catalog)
        # ensure this document participates even if not yet in the catalog
        graph.setdefault(flow_id, set())
        for node in flow_ref_nodes(document):
            child, _, error = resolve_child(node, catalog)
            if child is not None and isinstance(child.get("id"), str):
                graph[flow_id].add(child["id"])
        cycle = find_cycle(flow_id, graph)
        if cycle:
            errors.append(f"$.nodes: flow_ref cycle detected: {' -> '.join(cycle)}")

    return errors
