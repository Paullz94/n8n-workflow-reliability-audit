#!/usr/bin/env python3
"""Unified PCFlows paid-package fulfillment.

Consumes a provider-verified Stripe Checkout Session snapshot plus package inputs
and emits a privacy-bounded customer delivery.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

import ai_review_packet
import audit_make
import focused_risk_check
import fulfill_order
import order_contract
import portfolio_qa
import report_builder


class PackageFulfillmentError(ValueError):
    pass


def _sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def _load(path: Path, label: str) -> dict[str, Any]:
    try:
        value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:
        raise PackageFulfillmentError(f"{label} is not valid readable JSON: {exc}") from exc
    if not isinstance(value,dict):
        raise PackageFulfillmentError(f"{label} root must be an object")
    return value


def _ensure_empty(out_dir: Path) -> None:
    if out_dir.exists() and any(out_dir.iterdir()):
        raise PackageFulfillmentError("output directory must be empty")
    out_dir.mkdir(parents=True,exist_ok=True)


def _safe_scan(blueprint: dict[str,Any]) -> list[audit_make.Finding]:
    findings=audit_make.scan_blueprint(blueprint)
    if any(f.rule=="possible-secret-in-blueprint" for f in findings):
        raise PackageFulfillmentError(
            "Possible secret-like literal detected. Stop fulfillment and request a newly sanitized blueprint."
        )
    return findings


def build_focused_delivery(
    *,
    order: dict[str,Any],
    blueprint_path: Path,
    context_path: Path,
    focus: str | None,
    out_dir: Path,
) -> dict[str,Any]:
    checked=order_contract.validate_paid_order(order)
    if checked["package_id"]!="focused_risk_check":
        raise PackageFulfillmentError("order is not for focused_risk_check")

    blueprint=_load(blueprint_path,"blueprint")
    raw_context=_load(context_path,"context")
    context=report_builder.sanitize_context(raw_context)
    fulfill_order.validate_context(context)
    findings=_safe_scan(blueprint)
    effective_focus=(focus or str(raw_context.get("requested_focus") or "")).strip()
    if effective_focus not in focused_risk_check.FOCUS_RULES:
        raise PackageFulfillmentError(
            "focused_risk_check requires one focus: duplicates, silent_skips, recovery or ordering"
        )

    _ensure_empty(out_dir)
    report_path=out_dir/"pcflows-focused-risk-check.md"
    findings_path=out_dir/"pcflows-findings.json"
    context_out=out_dir/"pcflows-context-used.json"
    manifest_path=out_dir/"pcflows-manifest.json"

    report=focused_risk_check.render_focused_report(
        effective_focus,blueprint_path.name,blueprint,raw_context
    )
    report_path.write_text(report,encoding="utf-8")
    findings_path.write_text(json.dumps({
        "order_ref":checked["session_id"],
        "package_id":checked["package_id"],
        "focus":effective_focus,
        "summary":audit_make.summary(findings),
        "findings":[f.__dict__ for f in findings],
    },indent=2)+"\n",encoding="utf-8")
    context_out.write_text(json.dumps(context,indent=2)+"\n",encoding="utf-8")

    manifest={
        "order":checked,
        "focus":effective_focus,
        "blueprint_source_name":blueprint_path.name,
        "blueprint_sha256":_sha256(blueprint_path),
        "context_source_name":context_path.name,
        "context_sha256":_sha256(context_path),
        "delivery_files":{},
        "privacy":{
            "raw_blueprint_included":False,
            "production_credentials_required":False,
            "included_rescan":False,
        },
    }
    for p in (report_path,findings_path,context_out):
        manifest["delivery_files"][p.name]=_sha256(p)
    manifest_path.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    manifest["delivery_files"][manifest_path.name]=_sha256(manifest_path)

    zip_path=out_dir/"pcflows-focused-risk-check-delivery.zip"
    with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for p in (report_path,findings_path,context_out,manifest_path):
            z.write(p,arcname=p.name)

    return {
        "order_ref":checked["session_id"],
        "package_id":checked["package_id"],
        "focus":effective_focus,
        "zip":str(zip_path),
        "report":str(report_path),
        "manifest":str(manifest_path),
    }


def build_data_integrity_delivery(
    *,
    order: dict[str,Any],
    blueprint_path: Path,
    context_path: Path,
    out_dir: Path,
)->dict[str,Any]:
    checked=order_contract.validate_paid_order(order)
    if checked["package_id"]!="data_integrity_audit":
        raise PackageFulfillmentError("order is not for data_integrity_audit")
    try:
        result=fulfill_order.build_delivery(
            blueprint_path=blueprint_path,
            context_path=context_path,
            order_ref=checked["session_id"],
            out_dir=out_dir,
        )
    except fulfill_order.FulfillmentError as exc:
        raise PackageFulfillmentError(str(exc)) from exc
    result["package_id"]=checked["package_id"]
    return result


def build_portfolio_delivery(
    *,
    order: dict[str,Any],
    scenarios:list[tuple[str,Path,Path]],
    out_dir:Path,
)->dict[str,Any]:
    checked=order_contract.validate_paid_order(order)
    if checked["package_id"]!="portfolio_release_qa":
        raise PackageFulfillmentError("order is not for portfolio_release_qa")
    if not 1 <= len(scenarios) <= 3:
        raise PackageFulfillmentError("portfolio_release_qa supports 1 to 3 scenarios")

    loaded=[]
    internal_packets=[]
    source_manifest=[]
    for name,bp_path,ctx_path in scenarios:
        blueprint=_load(bp_path,f"{name} blueprint")
        context=_load(ctx_path,f"{name} context")
        sanitized=report_builder.sanitize_context(context)
        fulfill_order.validate_context(sanitized)
        _safe_scan(blueprint)
        loaded.append((name,blueprint,context))
        internal_packets.append((name,ai_review_packet.make_packet(blueprint,context)))
        source_manifest.append({
            "name":name,
            "blueprint_source_name":bp_path.name,
            "blueprint_sha256":_sha256(bp_path),
            "context_source_name":ctx_path.name,
            "context_sha256":_sha256(ctx_path),
        })

    _ensure_empty(out_dir)
    result=portfolio_qa.build_portfolio(loaded)
    report=portfolio_qa.render_portfolio(result)

    report_path=out_dir/"pcflows-portfolio-release-qa.md"
    summary_path=out_dir/"pcflows-portfolio-summary.json"
    manifest_path=out_dir/"pcflows-manifest.json"

    report_path.write_text(report,encoding="utf-8")
    summary_path.write_text(json.dumps({
        "order_ref":checked["session_id"],
        "package_id":checked["package_id"],
        "scenario_count":result["scenario_count"],
        "aggregate_summary":result["aggregate_summary"],
        "recurring_rules":result["recurring_rules"],
        "scenarios":[
            {
                "name":item["name"],
                "summary":item["summary"],
                "pack_selection":item["pack_selection"],
            }
            for item in result["scenarios"]
        ],
    },indent=2)+"\n",encoding="utf-8")

    internal_dir=out_dir/"internal-review"
    internal_dir.mkdir(exist_ok=True)
    internal_files={}
    for i,(name,packet) in enumerate(internal_packets,1):
        safe_name=f"{i:02d}-ai-review-packet.json"
        p=internal_dir/safe_name
        p.write_text(json.dumps({"scenario_name":name,"packet":packet},indent=2)+"\n",encoding="utf-8")
        internal_files[str(p.relative_to(out_dir))]=_sha256(p)

    manifest={
        "order":checked,
        "sources":source_manifest,
        "delivery_files":{
            report_path.name:_sha256(report_path),
            summary_path.name:_sha256(summary_path),
        },
        "internal_review_files":internal_files,
        "privacy":{
            "raw_blueprints_included":False,
            "ai_review_packets_in_customer_zip":False,
            "production_credentials_required":False,
            "max_scenarios":3,
            "included_combined_rescan_round":True,
        },
    }
    manifest_path.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")

    zip_path=out_dir/"pcflows-portfolio-release-qa-delivery.zip"
    with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for p in (report_path,summary_path,manifest_path):
            z.write(p,arcname=p.name)

    return {
        "order_ref":checked["session_id"],
        "package_id":checked["package_id"],
        "scenario_count":result["scenario_count"],
        "report":str(report_path),
        "manifest":str(manifest_path),
        "zip":str(zip_path),
    }


def main()->int:
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="package",required=True)

    p1=sub.add_parser("focused_risk_check")
    p1.add_argument("--order",type=Path,required=True)
    p1.add_argument("--blueprint",type=Path,required=True)
    p1.add_argument("--context",type=Path,required=True)
    p1.add_argument("--focus",choices=sorted(focused_risk_check.FOCUS_RULES))
    p1.add_argument("--out-dir",type=Path,required=True)

    p2=sub.add_parser("data_integrity_audit")
    p2.add_argument("--order",type=Path,required=True)
    p2.add_argument("--blueprint",type=Path,required=True)
    p2.add_argument("--context",type=Path,required=True)
    p2.add_argument("--out-dir",type=Path,required=True)

    p3=sub.add_parser("portfolio_release_qa")
    p3.add_argument("--order",type=Path,required=True)
    p3.add_argument("--scenario",action="append",nargs=3,metavar=("NAME","BLUEPRINT","CONTEXT"),required=True)
    p3.add_argument("--out-dir",type=Path,required=True)

    args=parser.parse_args()
    try:
        order=_load(args.order,"order")
        if args.package=="focused_risk_check":
            result=build_focused_delivery(order=order,blueprint_path=args.blueprint,context_path=args.context,focus=args.focus,out_dir=args.out_dir)
        elif args.package=="data_integrity_audit":
            result=build_data_integrity_delivery(order=order,blueprint_path=args.blueprint,context_path=args.context,out_dir=args.out_dir)
        else:
            scenarios=[(n,Path(b),Path(c)) for n,b,c in args.scenario]
            result=build_portfolio_delivery(order=order,scenarios=scenarios,out_dir=args.out_dir)
    except (PackageFulfillmentError,order_contract.OrderContractError) as exc:
        print(json.dumps({"error":str(exc)}))
        return 2

    print(json.dumps(result,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
