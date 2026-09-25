#!/usr/bin/env python3
"""Generate an automated PCFlows Portfolio / Release QA for up to 3 scenarios."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import audit_make
import pack_selector
import report_builder
import build_pack_report


class PortfolioError(ValueError):
    pass


def analyze_scenario(name: str, blueprint: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    sanitized=report_builder.sanitize_context(context)
    findings=audit_make.scan_blueprint(blueprint)
    if any(f.rule=="possible-secret-in-blueprint" for f in findings):
        raise PortfolioError(f"{name}: possible secret-like literal detected")
    selection=pack_selector.select_pack(context)
    if selection.get("pack_id"):
        report=build_pack_report.render_pack_report(selection["pack_id"],name,blueprint,context)
    else:
        report=report_builder.render_report(name,findings,sanitized)
    return {
        "name":name,
        "summary":audit_make.summary(findings),
        "findings":findings,
        "pack_selection":selection,
        "report":report,
    }


def build_portfolio(
    scenarios: list[tuple[str,dict[str,Any],dict[str,Any]]]
) -> dict[str,Any]:
    if not 1 <= len(scenarios) <= 3:
        raise PortfolioError("Portfolio / Release QA supports 1 to 3 scenarios")
    analyzed=[analyze_scenario(*item) for item in scenarios]

    aggregate={k:0 for k in ("critical","high","medium","low","info")}
    recurring={}
    for item in analyzed:
        for k,v in item["summary"].items():
            aggregate[k]=aggregate.get(k,0)+v
        seen=set()
        for f in item["findings"]:
            if f.rule not in seen:
                recurring.setdefault(f.rule,[]).append(item["name"])
                seen.add(f.rule)

    recurring={rule:names for rule,names in recurring.items() if len(names)>=2}

    return {
        "scenario_count":len(analyzed),
        "aggregate_summary":aggregate,
        "recurring_rules":recurring,
        "scenarios":analyzed,
    }


def render_portfolio(result: dict[str,Any]) -> str:
    a=result["aggregate_summary"]
    lines=[
        "# PCFlows Portfolio / Release QA",
        "",
        f"Scenarios reviewed: **{result['scenario_count']}**",
        f"Aggregate static findings: **{a['critical']} critical, {a['high']} high, {a['medium']} medium, {a['low']} low**.",
        "",
        "## Cross-scenario release view",
        "",
    ]
    if result["recurring_rules"]:
        lines.append("Recurring rule families across multiple scenarios:")
        for rule,names in sorted(result["recurring_rules"].items()):
            lines.append(f"- **{rule}** — {', '.join(names)}")
    else:
        lines.append("No deterministic rule appeared across more than one supplied scenario.")

    lines += [
        "",
        "## Release checklist",
        "",
        "- Every high/critical finding has an explicit disposition.",
        "- Duplicate/retry behavior is tested with stable synthetic business keys.",
        "- Failure paths are exercised before handoff.",
        "- Any human-approval boundary is verified.",
        "- No production credentials or private webhook URLs remain in exported artifacts.",
        "- Revised blueprints are re-scanned after remediation.",
        "",
        "## Scenario reports",
        "",
    ]
    for item in result["scenarios"]:
        lines += [
            f"### {item['name']}",
            "",
            f"Selected mode: **{item['pack_selection'].get('pack_id') or 'generic'}**",
            "",
            item["report"],
            "",
            "---",
            "",
        ]
    lines += [
        "## Scope limitation",
        "",
        "This portfolio QA aggregates deterministic static evidence from up to three sanitized blueprints. "
        "It does not prove runtime correctness or model cross-scenario transactional guarantees that are not exported in the blueprints.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--scenario",action="append",nargs=3,metavar=("NAME","BLUEPRINT","CONTEXT"),required=True)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        items=[]
        for name,bp_path,ctx_path in args.scenario:
            bp=json.loads(Path(bp_path).read_text(encoding="utf-8"))
            ctx=json.loads(Path(ctx_path).read_text(encoding="utf-8"))
            if not isinstance(bp,dict) or not isinstance(ctx,dict):
                raise PortfolioError("Blueprint and context roots must be objects")
            items.append((name,bp,ctx))
        result=build_portfolio(items)
        report=render_portfolio(result)
    except (OSError,json.JSONDecodeError,PortfolioError,ValueError) as exc:
        print(json.dumps({"error":str(exc)}))
        return 2
    if args.out:
        args.out.write_text(report,encoding="utf-8")
    else:
        print(report)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
