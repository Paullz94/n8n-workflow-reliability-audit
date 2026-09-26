#!/usr/bin/env python3
"""Reconcile a trusted Stripe snapshot into Northstar's strict journal.

The tool is deliberately dry-run by default. It accepts Stripe JSON that was
retrieved through an authenticated provider connection or a signature-verified
pipeline, normalizes only finalized financial events, and refuses to silently
rewrite an existing journal event.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import ledger_engine
import stripe_adapter


class ReconcileError(ValueError):
    pass


def load_json(path: Path, expected: type) -> Any:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReconcileError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, expected):
        raise ReconcileError(f"{path} must contain {expected.__name__}")
    return value


def financially_final(event: dict[str, Any]) -> bool:
    kind = str(event.get("kind") or "").lower()
    status = str(event.get("status") or "").lower()
    if kind == "payment":
        return status in ledger_engine.PAID_STATUSES
    if kind == "refund":
        return status in ledger_engine.REFUND_STATUSES
    return False


def _comparable(event: dict[str, Any]) -> dict[str, Any]:
    """Fields that must remain immutable once journaled."""
    return {
        key: event.get(key)
        for key in (
            "id", "kind", "currency", "amount_eur", "status", "provider_verified",
            "customer_class", "test", "provider", "payment_id"
        )
        if key in event
    }


def reconcile(
    journal: list[dict[str, Any]],
    stripe_items: list[dict[str, Any]],
    *,
    provider_verified: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not provider_verified:
        raise ReconcileError(
            "Stripe snapshot is not provider-verified. Retrieve it from the authenticated Stripe connection first."
        )

    existing = {}
    for event in journal:
        if not isinstance(event, dict) or not event.get("id"):
            raise ReconcileError("Existing journal contains an invalid event")
        event_id = str(event["id"])
        if event_id in existing:
            raise ReconcileError(f"Duplicate existing journal id: {event_id}")
        existing[event_id] = event

    normalized = stripe_adapter.normalize_many(
        stripe_items,
        provider_verified=True,
    )
    finalized = [event for event in normalized if financially_final(event)]

    additions: list[dict[str, Any]] = []
    unchanged: list[str] = []

    for event in finalized:
        event_id = str(event["id"])
        prior = existing.get(event_id)
        if prior is None:
            additions.append(event)
            existing[event_id] = event
            continue
        if _comparable(prior) != _comparable(event):
            raise ReconcileError(
                f"Provider event {event_id} conflicts with the append-only journal; manual reconciliation required"
            )
        unchanged.append(event_id)

    merged = list(journal) + additions
    totals = ledger_engine.calculate(merged)
    summary = {
        "normalized_provider_events": len(normalized),
        "finalized_provider_events": len(finalized),
        "added_event_ids": [event["id"] for event in additions],
        "unchanged_event_ids": unchanged,
        "ignored_nonfinal_count": len(normalized) - len(finalized),
        "totals": asdict(totals),
    }
    return merged, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stripe_snapshot", type=Path)
    parser.add_argument("--journal", type=Path, default=Path("ledger_journal.json"))
    parser.add_argument("--out-journal", type=Path)
    parser.add_argument(
        "--trusted-provider-snapshot",
        action="store_true",
        help="Required: confirm the JSON came from authenticated Stripe/plugin output or a signature-verified pipeline.",
    )
    args = parser.parse_args()

    try:
        raw = load_json(args.stripe_snapshot, list)
        journal = load_json(args.journal, list)
        merged, summary = reconcile(
            journal,
            raw,
            provider_verified=args.trusted_provider_snapshot,
        )
    except (ReconcileError, ledger_engine.LedgerError, stripe_adapter.StripeAdapterError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2

    # Dry-run unless an explicit output path is supplied. Never overwrite the
    # canonical journal implicitly.
    if args.out_journal:
        args.out_journal.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
