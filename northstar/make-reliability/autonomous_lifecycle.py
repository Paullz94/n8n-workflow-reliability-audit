#!/usr/bin/env python3
"""Deterministic PCFlows customer lifecycle / autonomy gate.

This module defines which states AI can progress without owner input once the
one-time legal/account prerequisites are satisfied.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Decision:
    action: str
    autonomous: bool
    reason: str
    next_state: str


OWNER_ONLY_GATES = {
    "identity_or_kyc": "Identity/KYC attestation must be completed by the account owner.",
    "legal_registration": "Official registration/VAT choices or attestations can require the legal owner.",
    "new_owner_spend": "New owner-capital spend requires explicit approval under Northstar policy.",
    "credential_connection": "Connecting a new third-party account requires owner authorization.",
    "material_dispute": "A legal/payment dispute or exceptional refund claim requires owner review if policy cannot resolve it.",
}


def decide(case: dict[str, Any]) -> Decision:
    state = str(case.get("state") or "").strip()
    blocked = str(case.get("blocked_by") or "").strip()

    if blocked in OWNER_ONLY_GATES:
        return Decision(
            action="request_owner_prerequisite",
            autonomous=False,
            reason=OWNER_ONLY_GATES[blocked],
            next_state=state or "blocked",
        )

    if state == "lead_discovered":
        if case.get("channel_allowed") is not True:
            return Decision("archive_research_only", True, "Channel rules do not permit autonomous commercial participation.", "research_only")
        if case.get("offer_fit") is not True:
            return Decision("archive_low_fit", True, "Prospect does not meet the current offer-fit threshold.", "closed_no_action")
        return Decision("prepare_and_send_channel_native_outreach", True, "High-fit prospect on an allowed connected channel.", "outreach_sent")

    if state == "inquiry_received":
        return Decision("answer_scope_and_route_to_free_preflight", True, "Standard product inquiry can be answered from published scope.", "awaiting_preflight_or_intake")

    if state == "preflight_complete":
        route = str(case.get("qualification_route") or "")
        if route == "free_preflight_sufficient":
            return Decision("send_free_result_no_upsell", True, "Static evidence does not justify paid review.", "closed_free")
        if route == "resanitize_required":
            return Decision("request_resanitized_blueprint", True, "Possible secret-like input must not proceed.", "awaiting_safe_input")
        if route == "invalid_input":
            return Decision("request_fresh_export", True, "Input is not a supported Make blueprint.", "awaiting_safe_input")
        if route in {"context_required", "paid_audit_candidate"}:
            return Decision("send_intake_or_checkout_path", True, "Qualified path can be handled from fixed product rules.", "awaiting_checkout_or_context")

    if state == "payment_detected":
        if case.get("provider_verified") is not True:
            return Decision("wait_for_provider_verification", True, "Unverified payment never enters fulfillment/revenue.", "awaiting_provider")
        if case.get("owner_or_test") is True:
            return Decision("exclude_from_revenue_and_test_only", True, "Owner/test payment is never target revenue.", "test_payment")
        return Decision("request_or_match_sanitized_intake", True, "Verified external payment can enter fulfillment.", "awaiting_files")

    if state == "files_received":
        if case.get("cross_case_mismatch") is True:
            return Decision("freeze_case_and_investigate", True, "Case binding mismatch must stop all outbound processing.", "privacy_hold")
        if case.get("secret_like") is True or case.get("personal_data_like") is True:
            return Decision("stop_and_request_resanitization", True, "Secret/customer-data gate hard-stops processing.", "awaiting_safe_input")
        if case.get("scope_fit") is not True:
            return Decision("cancel_or_refund_per_scope_policy", True, "Request is outside fixed scope before substantive delivery.", "refund_or_cancel")
        return Decision("run_audit_pipeline", True, "Safe in-scope files can be processed deterministically.", "qa_review")

    if state == "verified_repair_requested":
        if case.get("verified_repair_public_enabled") is not True:
            return Decision("route_to_audit_or_diagnostic", True, "Verified Repair is not publicly enabled until runtime gates pass.", "audit_or_diagnostic")
        if case.get("repair_eligible") is not True:
            return Decision("decline_verified_repair_or_diagnose_first", True, "The requested repair is not bounded/testable enough for a verified outcome.", "audit_or_diagnostic")
        return Decision("open_resolution_contract", True, "Bounded verified-repair request passed the deterministic intake gates.", "repair_contract")

    if state == "qa_review":
        if case.get("unsupported_claim_detected") is True:
            return Decision("remove_unsupported_claim_and_regenerate", True, "AI output must remain bounded by deterministic evidence.", "qa_review")
        return Decision("deliver_report", True, "Report passed deterministic/privacy QA.", "delivered")

    if state == "rescan_requested":
        return Decision("run_before_after_rescan", True, "One included re-scan is part of fixed scope.", "rescan_delivered")

    if state == "refund_requested":
        reason = str(case.get("refund_reason") or "")
        if reason in {"out_of_scope_before_delivery", "material_non_delivery", "duplicate_charge"}:
            return Decision("refund_via_provider_and_reconcile", True, "Request matches documented refund policy.", "refunded")
        return Decision("escalate_material_dispute", False, "Refund request is outside deterministic policy.", "refund_review")

    if state == "delivered":
        return Decision("send_bounded_followup_and_close_if_no_rescan", True, "Post-delivery support is bounded by the fixed pilot.", "awaiting_rescan_or_close")

    raise ValueError(f"Unsupported lifecycle state: {state!r}")
