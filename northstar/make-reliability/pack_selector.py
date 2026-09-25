#!/usr/bin/env python3
"""Select the most relevant PCFlows problem pack from safe business context.

This is a routing heuristic, not a claim about the customer's live system.
"""
from __future__ import annotations

from typing import Any

import report_builder


KEYWORDS = {
    "lead_flow": {
        "lead", "leads", "crm", "sales", "appointment", "booking", "follow-up",
        "followup", "sms", "prospect", "pipeline", "contact", "routing", "owner"
    },
    "invoice_payment": {
        "invoice", "invoices", "payment", "payments", "stripe", "quickbooks",
        "xero", "accounting", "paid", "refund", "balance", "billing", "customer match"
    },
    "ai_guardrails": {
        "ai", "llm", "openai", "claude", "gpt", "classification", "classify",
        "extract", "extraction", "prompt", "model", "human approval", "confidence"
    },
}


def select_pack(raw_context: dict[str, Any] | None) -> dict[str, Any]:
    context = report_builder.sanitize_context(raw_context or {})
    fragments: list[str] = []
    for key in ("scenario_name", "business_goal", "recovery_expectation"):
        value = context.get(key)
        if isinstance(value, str):
            fragments.append(value.lower())
    for value in context.get("critical_side_effects") or []:
        fragments.append(str(value).lower())
    text = " ".join(fragments)

    scores = {
        pack: sum(1 for keyword in words if keyword in text)
        for pack, words in KEYWORDS.items()
    }
    best = max(scores, key=scores.get) if scores else None
    best_score = scores.get(best, 0) if best else 0

    if best_score == 0:
        return {
            "pack_id": None,
            "route": "generic_data_integrity",
            "scores": scores,
            "reason": "No vertical has enough explicit safe-context evidence; use the generic audit.",
        }

    ties = [pack for pack, value in scores.items() if value == best_score]
    if len(ties) > 1:
        return {
            "pack_id": None,
            "route": "generic_data_integrity",
            "scores": scores,
            "reason": "Context spans multiple verticals with equal evidence; use generic audit unless later customer context resolves it.",
        }

    return {
        "pack_id": best,
        "route": "vertical_pack",
        "scores": scores,
        "reason": "Selected from explicit non-sensitive context keywords; selection does not infer live behavior.",
    }
