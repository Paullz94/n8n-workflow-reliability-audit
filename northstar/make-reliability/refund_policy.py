#!/usr/bin/env python3
"""Deterministic PCFlows refund decision policy.

The output is an instruction for the connected payment provider operator.
It does not itself move money.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RefundDecision:
    autonomous: bool
    action: str
    amount_mode: str
    reason: str


AUTO_FULL = {
    "duplicate_charge",
    "out_of_scope_before_delivery",
    "pcflows_cancelled_before_delivery",
    "material_non_delivery",
}

NO_AUTO = {
    "customer_changed_mind_after_custom_report",
    "disagrees_with_findings",
    "wants_implementation_included",
    "unknown",
}


def decide_refund(
    *,
    reason_code: str,
    payment_succeeded: bool,
    already_refunded: bool,
    substantive_delivery_started: bool,
    custom_report_delivered: bool,
) -> RefundDecision:
    reason = reason_code.strip().lower()

    if not payment_succeeded:
        return RefundDecision(True, "no_refund_needed", "none", "No successful payment exists to refund.")

    if already_refunded:
        return RefundDecision(True, "no_duplicate_refund", "none", "Provider already records the payment as refunded.")

    if reason == "duplicate_charge":
        return RefundDecision(True, "refund", "full", "Duplicate charge is a deterministic billing error.")

    if reason in {"out_of_scope_before_delivery", "pcflows_cancelled_before_delivery"}:
        if custom_report_delivered or substantive_delivery_started:
            return RefundDecision(False, "manual_exception_review", "undetermined", "Scope cancellation is no longer clearly pre-delivery.")
        return RefundDecision(True, "refund", "full", "PCFlows cannot deliver the documented fixed scope before substantive work.")

    if reason == "material_non_delivery":
        if custom_report_delivered:
            return RefundDecision(False, "manual_exception_review", "undetermined", "A custom report exists; determine whether delivery was materially deficient.")
        return RefundDecision(True, "refund", "full", "Documented service was materially not delivered.")

    if reason in NO_AUTO or reason not in AUTO_FULL:
        return RefundDecision(False, "manual_exception_review", "undetermined", "Request falls outside deterministic refund policy.")

    return RefundDecision(False, "manual_exception_review", "undetermined", "Refund state requires exceptional review.")
