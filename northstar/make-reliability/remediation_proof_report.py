#!/usr/bin/env python3
"""Build a conservative PCFlows remediation proof report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import compare_rescan
import fix_verification


class ProofReportError(ValueError):
    pass


def _evidence_key(item: dict[str,Any]) -> tuple[str,str]:
    return (str(item.get("rule") or ""), str(item.get("module_id") if item.get("module_id") is not None else ""))


def build_proof(
    before:dict[str,Any],
    after:dict[str,Any],
    evidence_items:list[dict[str,Any]]|None=None,
)->dict[str,Any]:
    comparison=compare_rescan.compare(before,after)
    evidence_map={}
    for item in evidence_items or []:
        if isinstance(item,dict):
            evidence_map[_evidence_key(item)]=item

    statuses=[]
    for row in comparison["resolved"]:
        key=(row["rule"],str(row.get("module_id") if row.get("module_id") is not None else ""))
        evidence=evidence_map.get(key)
        status=fix_verification.resolution_status(
            rule=row["rule"],
            still_present_after=False,
            evidence=evidence,
        )
        statuses.append({
            "rule":row["rule"],
            "module_id":row.get("module_id"),
            "module":row.get("module"),
            "status":status,
        })

    for row in comparison["remaining"]:
        key=(row["rule"],str(row.get("module_id") if row.get("module_id") is not None else ""))
        evidence=evidence_map.get(key)
        status=fix_verification.resolution_status(
            rule=row["rule"],
            still_present_after=True,
            evidence=evidence,
        )
        statuses.append({
            "rule":row["rule"],
            "module_id":row.get("module_id"),
            "module":row.get("module"),
            "status":status,
        })

    counts={}
    for item in statuses:
        name=item["status"]["status"]
        counts[name]=counts.get(name,0)+1

    return {
        "comparison_counts":comparison["counts"],
        "proof_counts":counts,
        "statuses":statuses,
        "new_findings":comparison["new"],
    }


def render_proof(result:dict[str,Any])->str:
    lines=[
        "# PCFlows Remediation Proof Report",
        "",
        "## Proof summary",
        "",
    ]
    for status,count in sorted(result["proof_counts"].items()):
        lines.append(f"- {status}: **{count}**")
    if not result["proof_counts"]:
        lines.append("- No prior findings were available for proof classification.")

    lines += ["","## Finding status",""]
    for item in result["statuses"]:
        s=item["status"]
        where=f" — {item['module']}" if item.get("module") else ""
        lines += [
            f"### {item['rule']}{where}",
            "",
            f"**Status:** {s['status']}",
            "",
            s["customer_language"],
            "",
        ]
        missing=(s.get("evidence") or {}).get("missing") or []
        if missing:
            lines += [
                "**Runtime assertions still required:**",
                *[f"- {x}" for x in missing],
                "",
            ]

    if result["new_findings"]:
        lines += [
            "## New static findings",
            "",
            "The revised blueprint introduced new review signals. These must be assessed before remediation can be considered complete.",
            "",
        ]
        for row in result["new_findings"]:
            lines.append(f"- **{row['severity'].upper()} · {row['rule']}**")

    lines += [
        "",
        "## Meaning of “verified fixed”",
        "",
        "For runtime-dependent findings, PCFlows uses that label only when the static signal is cleared and every rule-specific assertion passes in a connected synthetic test run that PCFlows can independently observe.",
        "",
    ]
    return "\n".join(lines)


def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("before",type=Path)
    parser.add_argument("after",type=Path)
    parser.add_argument("--evidence",type=Path)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        before=json.loads(args.before.read_text(encoding="utf-8"))
        after=json.loads(args.after.read_text(encoding="utf-8"))
        evidence=[]
        if args.evidence:
            raw=json.loads(args.evidence.read_text(encoding="utf-8"))
            if not isinstance(raw,list):
                raise ProofReportError("evidence root must be an array")
            evidence=raw
        result=build_proof(before,after,evidence)
        report=render_proof(result)
    except (OSError,json.JSONDecodeError,ProofReportError,compare_rescan.CompareError,fix_verification.VerificationError) as exc:
        print(json.dumps({"error":str(exc)}))
        return 2
    if args.out:
        args.out.write_text(report,encoding="utf-8")
    else:
        print(report)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
