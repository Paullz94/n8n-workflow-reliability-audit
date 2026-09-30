#!/usr/bin/env python3
"""Render a bounded EUR79 PCFlows Focused Risk Check."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import audit_make
import report_builder


FOCUS_RULES = {
    "duplicates": {
        "label": "Duplicate effects / idempotency",
        "rules": {
            "retrying-write-idempotency-review",
            "http-write-idempotency-review",
            "concurrency-review",
        },
    },
    "silent_skips": {
        "label": "Silent skips / missing work",
        "rules": {
            "filtered-write-silent-skip-review",
            "write-skip-handler-data-loss-review",
            "write-resume-handler-silent-success-review",
        },
    },
    "recovery": {
        "label": "Failure recovery",
        "rules": {
            "write-without-error-handler",
            "write-commit-partial-state-review",
            "rollback-limited-by-autocommit-review",
            "incomplete-executions-disabled-review",
            "data-loss-enabled",
        },
    },
    "ordering": {
        "label": "Concurrency / ordering",
        "rules": {
            "concurrency-review",
        },
    },
}


def render_focused_report(
    focus: str,
    source: str,
    blueprint: dict,
    raw_context: dict,
) -> str:
    if focus not in FOCUS_RULES:
        raise ValueError(f"Unknown focus: {focus}")
    context = report_builder.sanitize_context(raw_context)
    findings = audit_make.scan_blueprint(blueprint)
    if any(f.rule == "possible-secret-in-blueprint" for f in findings):
        raise ValueError("Possible secret-like literal detected; re-sanitize before report generation.")

    selected = [f for f in findings if f.rule in FOCUS_RULES[focus]["rules"]]
    selected = sorted(
        selected,
        key=lambda f: (-audit_make.SEVERITY_ORDER[f.severity], f.rule, f.path or ""),
    )[:6]

    lines = [
        "# PCFlows Focused Risk Check",
        "",
        f"Scenario: **{context.get('scenario_name') or source}**",
        f"Focus: **{FOCUS_RULES[focus]['label']}**",
        "",
        "## Result",
        "",
    ]

    if not selected:
        lines += [
            "No current deterministic finding matched this chosen focus.",
            "",
            "This does not prove the risk is absent at runtime.",
            "",
        ]
    else:
        enriched = report_builder.enriched_findings(selected, context)
        for i, row in enumerate(enriched, 1):
            f = row["finding"]
            g = row["guidance"]
            lines += [
                f"### {i}. {f.severity.upper()} · {f.rule}",
                "",
                f"**Evidence:** {f.message}",
                "",
                f"**Why it matters:** {g.impact}",
                "",
                f"**Next step:** {g.action}",
                "",
                f"**Synthetic verification:** {g.verify}",
                "",
            ]

    lines += [
        "## Scope",
        "",
        "This is a focused static review of one chosen risk area in one sanitized Make.com blueprint.",
        "It is not the full cross-category Data Integrity Audit and does not include a remediation re-scan.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("focus", choices=sorted(FOCUS_RULES))
    parser.add_argument("blueprint", type=Path)
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        bp=json.loads(args.blueprint.read_text(encoding="utf-8"))
        ctx=json.loads(args.context.read_text(encoding="utf-8"))
        if not isinstance(bp, dict) or not isinstance(ctx, dict):
            raise ValueError("Blueprint and context roots must be objects")
        report=render_focused_report(args.focus,args.blueprint.name,bp,ctx)
    except (OSError,json.JSONDecodeError,ValueError) as exc:
        print(json.dumps({"error":str(exc)}))
        return 2
    if args.out:
        args.out.write_text(report,encoding="utf-8")
    else:
        print(report)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
