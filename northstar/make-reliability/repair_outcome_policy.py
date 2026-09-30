#!/usr/bin/env python3
"""Outcome policy for the future PCFlows Verified Repair offer.

This does not issue a Stripe refund itself. It determines the required
commercial outcome from verified repair-case state.
"""
from __future__ import annotations

from typing import Any


class RepairOutcomeError(ValueError):
    pass


def decide_repair_outcome(case: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(case,dict):
        raise RepairOutcomeError("case must be an object")

    accepted=case.get("accepted_as_verified_repair") is True
    if not accepted:
        return {
            "outcome":"not_a_verified_repair_case",
            "refund_required":False,
            "customer_complete":False,
        }

    if case.get("critical_rollback_failure") is True:
        return {
            "outcome":"critical_incident_escalation",
            "refund_required":True,
            "customer_complete":False,
            "reason":"Production rollback failed. Do not mark complete; escalate incident handling and refund the repair fee.",
        }

    if case.get("all_issues_closed_verified") is True:
        return {
            "outcome":"verified_success",
            "refund_required":False,
            "customer_complete":True,
            "reason":"Every accepted issue contract is closed_verified.",
        }

    if case.get("customer_access_revoked") is True:
        return {
            "outcome":"blocked_by_customer_access",
            "refund_required":False,
            "customer_complete":False,
            "reason":"Repair cannot continue until the customer restores the explicitly required authorized access.",
        }

    if case.get("customer_changed_target_or_scope") is True:
        return {
            "outcome":"scope_changed",
            "refund_required":False,
            "customer_complete":False,
            "reason":"Do not silently redefine the accepted issue. Re-qualify the changed scope before continuing.",
        }

    if case.get("delivery_window_exhausted") is True:
        return {
            "outcome":"verified_fix_not_achieved",
            "refund_required":True,
            "customer_complete":False,
            "reason":"PCFlows accepted the issue for Verified Repair but did not reach closed_verified within the agreed bounded delivery window.",
        }

    return {
        "outcome":"repair_in_progress",
        "refund_required":False,
        "customer_complete":False,
        "reason":"At least one accepted issue remains open; continue repair/testing and do not claim completion.",
    }
