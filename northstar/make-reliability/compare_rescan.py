#!/usr/bin/env python3
"""Compare deterministic PCFlows findings before vs after remediation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import audit_make
import fix_verification


class CompareError(ValueError):
    pass


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CompareError(f"{label} is not valid readable JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise CompareError(f"{label} root must be an object")
    return value


def key(f: audit_make.Finding) -> tuple[str, str, str | None]:
    # Module IDs are normally more stable than list positions when a customer
    # inserts or reorders modules during remediation. Fall back to path only
    # when an exported finding has no module id.
    anchor = f"id:{f.module_id}" if f.module_id is not None else f"path:{f.path or ''}"
    return (f.rule, anchor, f.module)


def compare(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_findings = audit_make.scan_blueprint(before)
    after_findings = audit_make.scan_blueprint(after)

    if any(f.rule == "possible-secret-in-blueprint" for f in before_findings + after_findings):
        raise CompareError("Possible secret-like literal detected. Re-sanitize both blueprints before comparison.")

    before_map = {key(f): f for f in before_findings}
    after_map = {key(f): f for f in after_findings}

    resolved_keys = sorted(set(before_map) - set(after_map))
    remaining_keys = sorted(set(before_map) & set(after_map))
    new_keys = sorted(set(after_map) - set(before_map))

    def rows(keys, source, state):
        out=[]
        for k in keys:
            f=source[k]
            row={
                "rule": f.rule,
                "severity": f.severity,
                "message": f.message,
                "module_id": f.module_id,
                "module": f.module,
                "path": f.path,
            }
            if state=="resolved":
                row["verification"]=fix_verification.resolution_status(
                    rule=f.rule,
                    still_present_after=False,
                )
            elif state=="remaining":
                row["verification"]=fix_verification.resolution_status(
                    rule=f.rule,
                    still_present_after=True,
                )
            else:
                row["verification"]={
                    "status":"new_detected",
                    "verified_fixed":False,
                    "customer_language":"This static review signal is new in the revised blueprint.",
                }
            out.append(row)
        return out

    return {
        "before_summary": audit_make.summary(before_findings),
        "after_summary": audit_make.summary(after_findings),
        "resolved": rows(resolved_keys, before_map, "resolved"),
        "remaining": rows(remaining_keys, after_map, "remaining"),
        "new": rows(new_keys, after_map, "new"),
        "counts": {
            "resolved": len(resolved_keys),
            "remaining": len(remaining_keys),
            "new": len(new_keys),
        },
    }


def render_markdown(result: dict[str, Any]) -> str:
    c = result["counts"]
    lines = [
        "# PCFlows Remediation Re-scan",
        "",
        f"Statically cleared findings: **{c['resolved']}**",
        f"Remaining findings: **{c['remaining']}**",
        f"New findings: **{c['new']}**",
        "",
    ]

    for title, key_name in (
        ("Statically cleared", "resolved"),
        ("Remaining", "remaining"),
        ("New", "new"),
    ):
        lines += [f"## {title}", ""]
        rows = result[key_name]
        if not rows:
            lines += ["None.", ""]
            continue
        for row in rows:
            where = f" — {row['module']}" if row.get("module") else ""
            lines += [
                f"- **{row['severity'].upper()} · {row['rule']}**{where}",
                f"  - {row['message']}",
            ]
            verification=row.get("verification") or {}
            if verification.get("customer_language"):
                lines += [f"  - Proof status: {verification['customer_language']}"]
        lines.append("")

    lines += [
        "## Interpretation",
        "",
        "A statically cleared finding means only that the revised blueprint no longer matches that deterministic rule. Runtime-dependent findings remain unverified until their rule-specific synthetic execution checks pass. PCFlows must not call them fixed before that proof exists.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    try:
        result = compare(
            load_object(args.before, "before blueprint"),
            load_object(args.after, "after blueprint"),
        )
    except CompareError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2

    if args.json_out:
        args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if args.md_out:
        args.md_out.write_text(render_markdown(result), encoding="utf-8")
    if not args.json_out and not args.md_out:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
