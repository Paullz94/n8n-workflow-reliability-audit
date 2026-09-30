#!/usr/bin/env python3
"""Select the most relevant PCFlows problem pack from safe business context.

This is a conservative routing heuristic, not a claim about the customer's
live system. Whole-word/phrase matching avoids accidental substring matches
(e.g. "ai" inside "daily").
"""
from __future__ import annotations

import re
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
        "extract", "extraction", "prompt", "model", "human approval", "confidence",
        "malformed", "uncertain"
    },
    "client_onboarding": {
        "onboarding", "onboard", "welcome", "kickoff", "project setup", "folder",
        "provisioning", "client setup", "new customer", "implementation kickoff"
    },
}


def _matches(text: str, keyword: str) -> bool:
    phrase=keyword.strip().lower()
    if not phrase:
        return False
    pattern=r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])"
    return re.search(pattern,text,re.I) is not None


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
        pack: sum(1 for keyword in words if _matches(text,keyword))
        for pack, words in KEYWORDS.items()
    }

    # AI + finance is deliberately treated as cross-domain unless later context
    # resolves whether the main risk is model-output safety or financial sync.
    ai_finance_ambiguous=(
        scores["ai_guardrails"]>0
        and scores["invoice_payment"]>0
        and _matches(text,"ai")
        and any(_matches(text,k) for k in ("invoice","invoices","payment","payments"))
    )
    if ai_finance_ambiguous:
        return {
            "pack_id": None,
            "route": "generic_data_integrity",
            "scores": scores,
            "reason": "Context clearly spans both AI and finance/payment risk; use generic audit unless later context resolves the dominant failure boundary.",
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
        "reason": "Selected from explicit non-sensitive whole-word/phrase context signals; selection does not infer live behavior.",
    }
