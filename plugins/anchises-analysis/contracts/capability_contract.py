"""Build/test-time capability checks; never a runtime MCP proxy or dispatcher."""
from __future__ import annotations

import json
from pathlib import Path


def load_capabilities():
    # JSON is a YAML subset; retain a zero-dependency metadata reader.
    return json.loads(Path(__file__).with_name("capabilities.yaml").read_text())


def required_tools():
    return {
        name for group in load_capabilities()["groups"].values()
        for name in group["tools"]
    }


def _semantic(value):
    if isinstance(value, dict):
        return {k: ({name: _semantic(schema) for name, schema in v.items()}
                    if k in {"properties", "patternProperties", "$defs", "definitions"}
                    and isinstance(v, dict) else _semantic(v)) for k, v in value.items()
                if k not in {"description", "title", "examples", "$comment"}}
    if isinstance(value, list):
        return [_semantic(v) for v in value]
    return value


def compatibility_changes(previous, current):
    """Conservative release gate, not a complete JSON Schema subsumption proof.

    Additive tools and optional input properties are review notices. Changed
    constraints, security, existing outputs, or required inputs block automatic
    acceptance until maintainers revise the workflow and its tests.
    """
    old = {t["name"]: t for t in previous["tools"]}
    new = {t["name"]: t for t in current["tools"]}
    blocking, notices = [], []
    for name in sorted(required_tools() - new.keys()):
        blocking.append(f"missing required tool: {name}")
    for name in sorted(new.keys() - old.keys()):
        notices.append(f"new tool requires workflow review: {name}")
    for name in sorted(old.keys() & new.keys()):
        before, after = old[name], new[name]
        a, b = _semantic(before["inputSchema"]), _semantic(after["inputSchema"])
        optional_added = set(b.get("properties", {})) - set(a.get("properties", {}))
        for field in optional_added - set(b.get("required", [])):
            b["properties"].pop(field)
            notices.append(f"optional input added: {name}.{field}")
        if a != b:
            blocking.append(f"input schema changed: {name}")
        for field in ("outputSchema", "securitySchemes", "annotations"):
            if _semantic(before.get(field)) != _semantic(after.get(field)):
                blocking.append(f"{field} changed: {name}")
    return {"blocking": blocking, "notices": notices}
