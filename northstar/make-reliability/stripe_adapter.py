#!/usr/bin/env python3
"""Normalize trusted Stripe PaymentIntent/Refund data into Northstar journal events.

This module does not verify Stripe webhook signatures and therefore defaults
provider_verified to False. Production callers must set it True only after
retrieving objects from an authenticated Stripe account or after successful
Stripe webhook signature verification upstream.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path
from typing import Any


class StripeAdapterError(ValueError):
    pass


def _cents_to_eur(value: Any) -> float:
    try:
        cents = int(value)
    except (TypeError, ValueError) as exc:
        raise StripeAdapterError(f"Invalid Stripe amount: {value!r}") from exc
    if cents < 0:
        raise StripeAdapterError("Stripe amount must be non-negative")
    return float((Decimal(cents) / Decimal(100)).quantize(Decimal("0.01")))


def _truthy(value: Any) -> bool:
    if value is True or value == 1:
        return True
    return isinstance(value, str) and value.strip().lower() in {"1", "true", "yes"}


def _object_from_event(item: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    if not isinstance(item, dict):
        raise StripeAdapterError("Stripe item must be an object")
    if isinstance(item.get("data"), dict) and isinstance(item["data"].get("object"), dict):
        return str(item.get("type") or "") or None, item["data"]["object"]
    return None, item


def normalize_item(item: dict[str, Any], *, provider_verified: bool = False) -> dict[str, Any] | None:
    event_type, obj = _object_from_event(item)
    object_type = str(obj.get("object") or "")

    if object_type == "payment_intent" or event_type == "payment_intent.succeeded":
        if str(obj.get("status") or "").lower() != "succeeded":
            return None
        currency = str(obj.get("currency") or "").upper()
        if currency != "EUR":
            raise StripeAdapterError("Northstar pilot accepts EUR Stripe payments only")
        payment_id = str(obj.get("id") or "").strip()
        if not payment_id:
            raise StripeAdapterError("Stripe PaymentIntent is missing id")
        amount = obj.get("amount_received")
        if amount is None:
            amount = obj.get("amount")
        metadata = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
        livemode = obj.get("livemode") is True
        explicit_test = _truthy(metadata.get("northstar_test"))
        owner = _truthy(metadata.get("northstar_owner"))
        return {
            "id": payment_id,
            "kind": "payment",
            "currency": "EUR",
            "amount_eur": _cents_to_eur(amount),
            "status": "succeeded",
            "provider_verified": bool(provider_verified),
            "customer_class": "owner" if owner else "external",
            "test": (not livemode) or explicit_test,
            "provider": "stripe",
        }

    if object_type == "refund" or (event_type and event_type.startswith("refund.")):
        currency = str(obj.get("currency") or "").upper()
        if currency != "EUR":
            raise StripeAdapterError("Northstar pilot accepts EUR Stripe refunds only")
        refund_id = str(obj.get("id") or "").strip()
        payment_intent = obj.get("payment_intent")
        if isinstance(payment_intent, dict):
            payment_intent = payment_intent.get("id")
        payment_id = str(payment_intent or "").strip()
        if not refund_id or not payment_id:
            raise StripeAdapterError("Stripe Refund needs id and payment_intent")
        return {
            "id": refund_id,
            "kind": "refund",
            "currency": "EUR",
            "payment_id": payment_id,
            "amount_eur": _cents_to_eur(obj.get("amount")),
            "status": str(obj.get("status") or "").lower(),
            "provider": "stripe",
        }

    return None


def normalize_many(items: list[dict[str, Any]], *, provider_verified: bool = False) -> list[dict[str, Any]]:
    # Canonical object IDs are used as journal IDs. If an export contains
    # multiple webhook lifecycle events for the same object, the last object
    # state wins rather than creating duplicate financial events.
    normalized: dict[str, dict[str, Any]] = {}
    for item in items:
        event = normalize_item(item, provider_verified=provider_verified)
        if event is not None:
            normalized[event["id"]] = event
    return list(normalized.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stripe_json", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--provider-verified",
        action="store_true",
        help="Use only for authenticated Stripe API/plugin output or signature-verified webhooks.",
    )
    args = parser.parse_args()
    try:
        raw = json.loads(args.stripe_json.read_text(encoding="utf-8"))
        items = raw if isinstance(raw, list) else [raw]
        events = normalize_many(items, provider_verified=args.provider_verified)
    except (OSError, json.JSONDecodeError, StripeAdapterError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    payload = json.dumps(events, indent=2) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
