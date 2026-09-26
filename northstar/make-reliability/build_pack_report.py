#!/usr/bin/env python3
"""Render a PCFlows problem-specific audit report from the shared core."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import audit_make
import report_builder
import vertical_packs


def render_pack_report(
    pack_id: str,
    source: str,
    blueprint: dict,
    raw_context: dict,
) -> str:
    pack = vertical_packs.get_pack(pack_id)
    context = report_builder.sanitize_context(raw_context)
    findings = audit_make.scan_blueprint(blueprint)

    if any(f.rule == "possible-secret-in-blueprint" for f in findings):
        raise ValueError("Possible secret-like literal detected; re-sanitize before report generation.")

    core = report_builder.render_report(source, findings, context)
    plan = vertical_packs.build_pack_plan(pack_id, findings, raw_context)

    lines = [
        core.rstrip(),
        "",
        "---",
        "",
        f"## {pack.name} — problem-specific layer",
        "",
        pack.buyer_problem,
        "",
        "### Pack-specific acceptance tests",
        "",
    ]

    for test in plan["acceptance_tests"]:
        lines += [
            f"#### {test['problem']}",
            "",
            f"**Synthetic test:** {test['test']}",
            "",
            f"**Pass condition:** {test['pass']}",
            "",
        ]

    lines += [
        "### Context questions to resolve before sign-off",
        "",
    ]
    for prompt in plan["context_prompts"]:
        lines.append(f"- {prompt}")

    lines += [
        "",
        "### Pack limitation",
        "",
        plan["static_limit"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pack", choices=sorted(vertical_packs.PACKS))
    parser.add_argument("blueprint", type=Path)
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    try:
        blueprint = json.loads(args.blueprint.read_text(encoding="utf-8"))
        raw_context = json.loads(args.context.read_text(encoding="utf-8"))
        if not isinstance(blueprint, dict) or not isinstance(raw_context, dict):
            raise ValueError("Blueprint and context roots must be JSON objects")
        report = render_pack_report(args.pack, args.blueprint.name, blueprint, raw_context)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2

    if args.out:
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
