#!/usr/bin/env python3
"""Strict append-only Northstar financial ledger calculator.

The journal is intentionally provider-agnostic. Real payment-provider exports
must be normalized into these events; the engine never treats an order form,
invoice promise, test payment or owner transaction as target revenue.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any

CENT = Decimal("0.01")
OWNER_RESERVE = Decimal("500.00")
TARGET = Decimal("1000.00")
PAID_STATUSES = {"paid", "succeeded", "settled"}
REFUND_STATUSES = {"succeeded", "settled", "refunded"}


class LedgerError(ValueError):
    pass


def money(value: Any) -> Decimal:
    try:
        amount = Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise LedgerError(f"Invalid money amount: {value!r}") from exc
    if amount < 0:
        raise LedgerError("Money amounts must be non-negative")
    return amount


def eur(value: Decimal) -> float:
    return float(value.quantize(CENT, rounding=ROUND_HALF_UP))


@dataclass
class Totals:
    target_verified_gross_revenue: float
    target_remaining: float
    owner_reserve_uninjected: float
    owner_capital_injected: float
    provider_collected_external_gross: float
    business_generated_cash: float
    verified_gross_revenue: float
    revenue_reinvested: float
    expenses: float
    refunds: float
    net_revenue: float
    net_operating_result: float
    target_reached: bool
    eligible_payment_count: int
    disqualified_payment_count: int


def _unique_events(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for event in events:
        if not isinstance(event, dict):
            raise LedgerError("Every journal event must be an object")
        event_id = str(event.get("id") or "").strip()
        if not event_id:
            raise LedgerError("Every journal event needs a stable id")
        if event_id in indexed:
            raise LedgerError(f"Duplicate event id: {event_id}")
        indexed[event_id] = event
    return indexed


def calculate(events: list[dict[str, Any]]) -> Totals:
    indexed = _unique_events(events)
    payments: dict[str, dict[str, Any]] = {}
    refunds_by_payment: dict[str, Decimal] = {}
    refund_present: set[str] = set()
    all_refunds = Decimal("0")
    owner_capital = Decimal("0")
    expenses = Decimal("0")
    revenue_reinvested = Decimal("0")

    for event_id, event in indexed.items():
        kind = str(event.get("kind") or "").lower()
        currency = str(event.get("currency") or "EUR").upper()
        if currency != "EUR":
            raise LedgerError(f"{event_id}: only EUR is supported in the zero-capital pilot")

        if kind == "payment":
            payments[event_id] = event
        elif kind == "refund":
            payment_id = str(event.get("payment_id") or "")
            if not payment_id:
                raise LedgerError(f"{event_id}: refund needs payment_id")
            status = str(event.get("status") or "").lower()
            if status in REFUND_STATUSES:
                amount = money(event.get("amount_eur", 0))
                refunds_by_payment[payment_id] = refunds_by_payment.get(payment_id, Decimal("0")) + amount
                refund_present.add(payment_id)
                all_refunds += amount
        elif kind == "expense":
            status = str(event.get("status") or "confirmed").lower()
            if status not in {"confirmed", "paid", "settled"}:
                continue
            amount = money(event.get("amount_eur", 0))
            expenses += amount
            funded_by = str(event.get("funded_by") or "business_revenue").lower()
            if funded_by == "business_revenue":
                revenue_reinvested += amount
            elif funded_by != "owner_capital":
                raise LedgerError(f"{event_id}: funded_by must be business_revenue or owner_capital")
        elif kind == "owner_capital":
            status = str(event.get("status") or "").lower()
            if status not in {"confirmed", "settled"}:
                continue
            if event.get("approved_by_paul") is not True:
                raise LedgerError(f"{event_id}: owner capital requires explicit approved_by_paul=true")
            owner_capital += money(event.get("amount_eur", 0))
        else:
            raise LedgerError(f"{event_id}: unsupported event kind {kind!r}")

    if owner_capital > OWNER_RESERVE:
        raise LedgerError("Owner capital exceeds the EUR 500 reserve ceiling")

    collected_external = Decimal("0")
    target_verified = Decimal("0")
    net_external = Decimal("0")
    eligible_count = 0
    disqualified_count = 0

    for payment_id, payment in payments.items():
        amount = money(payment.get("amount_eur", 0))
        status = str(payment.get("status") or "").lower()
        provider_verified = payment.get("provider_verified") is True
        is_test = payment.get("test") is True
        customer_class = str(payment.get("customer_class") or "external").lower()
        is_external = customer_class == "external"

        base_eligible = status in PAID_STATUSES and provider_verified and not is_test and is_external and amount > 0
        if not base_eligible:
            disqualified_count += 1
            continue

        refund_amount = refunds_by_payment.get(payment_id, Decimal("0"))
        if refund_amount > amount:
            raise LedgerError(f"Refunds exceed payment amount for {payment_id}")

        collected_external += amount
        net_external += amount - refund_amount

        # Strict target policy: any completed refund disqualifies the entire
        # transaction from the EUR 1,000 gross-revenue target.
        if payment_id in refund_present:
            disqualified_count += 1
        else:
            target_verified += amount
            eligible_count += 1

    for payment_id in refund_present:
        if payment_id not in payments:
            raise LedgerError(f"Refund references unknown payment: {payment_id}")

    business_cash = net_external - revenue_reinvested
    net_operating = net_external - expenses
    remaining = max(TARGET - target_verified, Decimal("0"))

    return Totals(
        target_verified_gross_revenue=eur(target_verified),
        target_remaining=eur(remaining),
        owner_reserve_uninjected=eur(OWNER_RESERVE - owner_capital),
        owner_capital_injected=eur(owner_capital),
        provider_collected_external_gross=eur(collected_external),
        business_generated_cash=eur(business_cash),
        verified_gross_revenue=eur(target_verified),
        revenue_reinvested=eur(revenue_reinvested),
        expenses=eur(expenses),
        refunds=eur(all_refunds),
        net_revenue=eur(net_external),
        net_operating_result=eur(net_operating),
        target_reached=target_verified >= TARGET,
        eligible_payment_count=eligible_count,
        disqualified_payment_count=disqualified_count,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("journal", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        raw = json.loads(args.journal.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise LedgerError("Journal root must be an array")
        totals = calculate(raw)
    except (OSError, json.JSONDecodeError, LedgerError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    payload = json.dumps(asdict(totals), indent=2) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
