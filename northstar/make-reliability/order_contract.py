#!/usr/bin/env python3
"""Strict provider-backed PCFlows package order contract."""
from __future__ import annotations

from typing import Any


class OrderContractError(ValueError):
    pass


PACKAGE_AMOUNTS_CENTS = {
    "focused_risk_check": 7900,
    "data_integrity_audit": 14900,
    "portfolio_release_qa": 39900,
}


def validate_paid_order(snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise OrderContractError("order snapshot must be an object")

    if snapshot.get("provider_verified") is not True:
        raise OrderContractError("order snapshot is not provider-verified")
    if snapshot.get("livemode") is not True:
        raise OrderContractError("only live external payments can enter paid fulfillment")

    session_id = str(snapshot.get("session_id") or snapshot.get("id") or "").strip()
    if not session_id.startswith("cs_"):
        raise OrderContractError("missing valid Stripe Checkout Session id")

    payment_status = str(snapshot.get("payment_status") or "").lower()
    if payment_status != "paid":
        raise OrderContractError("Stripe Checkout Session is not paid")

    currency = str(snapshot.get("currency") or "").lower()
    if currency != "eur":
        raise OrderContractError("PCFlows paid packages require EUR")

    metadata = snapshot.get("metadata") or {}
    if not isinstance(metadata, dict):
        raise OrderContractError("metadata must be an object")
    package_id = str(metadata.get("pcflows_package") or "").strip()
    if package_id not in PACKAGE_AMOUNTS_CENTS:
        raise OrderContractError("missing or unsupported pcflows_package metadata")

    try:
        amount_total = int(snapshot.get("amount_total"))
    except (TypeError, ValueError) as exc:
        raise OrderContractError("amount_total must be an integer in cents") from exc

    expected = PACKAGE_AMOUNTS_CENTS[package_id]
    if amount_total != expected:
        raise OrderContractError(
            f"amount/package mismatch: {package_id} expects {expected} cents, got {amount_total}"
        )

    if snapshot.get("owner_or_test") is True:
        raise OrderContractError("owner/test payment cannot enter customer fulfillment")

    return {
        "session_id": session_id,
        "package_id": package_id,
        "amount_total": amount_total,
        "currency": currency,
        "provider_verified": True,
        "livemode": True,
    }
