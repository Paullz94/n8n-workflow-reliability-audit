#!/usr/bin/env python3
"""Compare up to three scenario pairs for PCFlows Portfolio / Release QA."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import compare_rescan
import portfolio_qa


class PortfolioRescanError(ValueError):
    pass


def compare_portfolio(
    pairs:list[tuple[str,dict[str,Any],dict[str,Any]]]
)->dict[str,Any]:
    if not 1 <= len(pairs) <= 3:
        raise PortfolioRescanError("Portfolio re-scan supports 1 to 3 scenario pairs")

    scenarios=[]
    totals={"resolved":0,"remaining":0,"new":0}
    for name,before,after in pairs:
        try:
            result=compare_rescan.compare(before,after)
        except compare_rescan.CompareError as exc:
            raise PortfolioRescanError(f"{name}: {exc}") from exc
        for key in totals:
            totals[key]+=result["counts"][key]
        scenarios.append({"name":name,"comparison":result})

    return {
        "scenario_count":len(scenarios),
        "totals":totals,
        "scenarios":scenarios,
    }


def render_portfolio_rescan(result:dict[str,Any])->str:
    t=result["totals"]
    lines=[
        "# PCFlows Portfolio Remediation Re-scan",
        "",
        f"Scenarios compared: **{result['scenario_count']}**",
        f"Resolved static findings: **{t['resolved']}**",
        f"Remaining static findings: **{t['remaining']}**",
        f"New static findings: **{t['new']}**",
        "",
        "## Scenario comparisons",
        "",
    ]
    for item in result["scenarios"]:
        lines += [
            f"### {item['name']}",
            "",
            compare_rescan.render_markdown(item["comparison"]),
            "",
            "---",
            "",
        ]
    lines += [
        "## Release interpretation",
        "",
        "A static finding marked resolved means the revised blueprint no longer matches that deterministic rule. "
        "It does not prove the live production issue is fixed. Re-run the original synthetic acceptance tests before release/handoff.",
        "",
    ]
    return "\n".join(lines)


def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--pair",action="append",nargs=3,metavar=("NAME","BEFORE","AFTER"),required=True)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        pairs=[]
        for name,before_path,after_path in args.pair:
            before=json.loads(Path(before_path).read_text(encoding="utf-8"))
            after=json.loads(Path(after_path).read_text(encoding="utf-8"))
            if not isinstance(before,dict) or not isinstance(after,dict):
                raise PortfolioRescanError("Blueprint roots must be objects")
            pairs.append((name,before,after))
        result=compare_portfolio(pairs)
        report=render_portfolio_rescan(result)
    except (OSError,json.JSONDecodeError,PortfolioRescanError,ValueError) as exc:
        print(json.dumps({"error":str(exc)}))
        return 2
    if args.out:
        args.out.write_text(report,encoding="utf-8")
    else:
        print(report)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
