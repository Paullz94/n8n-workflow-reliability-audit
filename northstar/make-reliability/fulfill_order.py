#!/usr/bin/env python3
"""Build a privacy-bounded PCFlows paid-audit delivery package.

This command is intentionally offline. It consumes:
- a sanitized Make.com blueprint JSON;
- a small allowlisted intake/context JSON;
- a Stripe Checkout Session/order reference supplied by the operator.

It never copies the raw blueprint into the delivery bundle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

import ai_review_packet
import audit_make
import build_pack_report
import customer_claim_guard
import pack_selector
import report_builder

ORDER_REF_RE = re.compile(r"^cs_[A-Za-z0-9_]+$")
REQUIRED_CONTEXT = ("scenario_name", "business_goal")


class FulfillmentError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_order_ref(order_ref: str) -> str:
    value = order_ref.strip()
    if not ORDER_REF_RE.fullmatch(value):
        raise FulfillmentError("order_ref must be a Stripe Checkout Session id beginning with cs_")
    return value


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FulfillmentError(f"{label} is not valid readable JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise FulfillmentError(f"{label} root must be a JSON object")
    return raw


def validate_context(context: dict[str, Any]) -> None:
    for key in REQUIRED_CONTEXT:
        value = context.get(key)
        if not isinstance(value, str) or not value.strip():
            raise FulfillmentError(f"context requires non-empty {key}")


def has_secret_finding(findings: list[audit_make.Finding]) -> bool:
    return any(f.rule == "possible-secret-in-blueprint" for f in findings)


def build_delivery(
    *,
    blueprint_path: Path,
    context_path: Path,
    order_ref: str,
    out_dir: Path,
) -> dict[str, Any]:
    order_ref = validate_order_ref(order_ref)
    blueprint = load_json_object(blueprint_path, "blueprint")
    raw_context = load_json_object(context_path, "context")
    context = report_builder.sanitize_context(raw_context)
    validate_context(context)

    findings = audit_make.scan_blueprint(blueprint)
    if has_secret_finding(findings):
        raise FulfillmentError(
            "Possible secret-like literal detected. Stop fulfillment and request a newly sanitized blueprint."
        )

    if out_dir.exists() and any(out_dir.iterdir()):
        raise FulfillmentError("output directory must be empty")
    out_dir.mkdir(parents=True, exist_ok=True)

    report_path = out_dir / "pcflows-data-integrity-audit.md"
    findings_path = out_dir / "pcflows-findings.json"
    context_path_out = out_dir / "pcflows-context-used.json"
    manifest_path = out_dir / "pcflows-manifest.json"
    ai_packet_path = out_dir / "pcflows-ai-review-packet.json"

    selection = pack_selector.select_pack(raw_context)
    if selection.get("pack_id"):
        report = build_pack_report.render_pack_report(
            selection["pack_id"],
            blueprint_path.name,
            blueprint,
            raw_context,
        )
    else:
        report = report_builder.render_report(blueprint_path.name, findings, context)
    try:
        customer_claim_guard.assert_safe_report(report)
    except customer_claim_guard.ClaimGuardError as exc:
        raise FulfillmentError(str(exc)) from exc
    report_path.write_text(report, encoding="utf-8")
    findings_payload = {
        "order_ref": order_ref,
        "summary": audit_make.summary(findings),
        "findings": [asdict(f) for f in findings],
    }
    findings_path.write_text(json.dumps(findings_payload, indent=2) + "\n", encoding="utf-8")
    context_path_out.write_text(json.dumps(context, indent=2) + "\n", encoding="utf-8")
    ai_packet = ai_review_packet.make_packet(blueprint, raw_context)
    ai_packet_path.write_text(json.dumps(ai_packet, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "order_ref": order_ref,
        "blueprint_source_name": blueprint_path.name,
        "blueprint_sha256": sha256_file(blueprint_path),
        "context_source_name": context_path.name,
        "context_sha256": sha256_file(context_path),
        "pack_selection": selection,
        "delivery_files": {
            report_path.name: sha256_file(report_path),
            findings_path.name: sha256_file(findings_path),
            context_path_out.name: sha256_file(context_path_out),
        },
        "internal_review_files": {
            ai_packet_path.name: sha256_file(ai_packet_path),
        },
        "privacy": {
            "raw_blueprint_included": False,
            "ai_review_packet_included_in_customer_zip": False,
            "production_credentials_required": False,
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    zip_path = out_dir / "pcflows-audit-delivery.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in (report_path, findings_path, context_path_out, manifest_path):
            archive.write(path, arcname=path.name)

    return {
        "order_ref": order_ref,
        "report": str(report_path),
        "findings": str(findings_path),
        "manifest": str(manifest_path),
        "ai_review_packet": str(ai_packet_path),
        "zip": str(zip_path),
        "finding_summary": audit_make.summary(findings),
        "pack_selection": selection,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("blueprint", type=Path)
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--order-ref", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    try:
        result = build_delivery(
            blueprint_path=args.blueprint,
            context_path=args.context,
            order_ref=args.order_ref,
            out_dir=args.out_dir,
        )
    except FulfillmentError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
