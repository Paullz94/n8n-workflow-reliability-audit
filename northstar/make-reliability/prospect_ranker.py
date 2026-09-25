#!/usr/bin/env python3
"""Rank public acquisition signals for PCFlows without contacting anyone."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class QueueError(ValueError):
    pass


def score(item: dict[str, Any]) -> int:
    positive = sum(int(item.get(k, 0)) for k in (
        "problem_fit", "audit_first_fit", "budget_signal", "freshness"
    ))
    negative = sum(int(item.get(k, 0)) for k in (
        "competition_penalty", "proof_gap_penalty"
    ))
    return positive - negative


def rank_queue(doc: dict[str, Any], *, contactable_only: bool = False) -> list[dict[str, Any]]:
    if not isinstance(doc, dict) or not isinstance(doc.get("prospects"), list):
        raise QueueError("Queue must contain a prospects array")

    launch_enabled = doc.get("launch_enabled") is True
    ranked = []
    for raw in doc["prospects"]:
        if not isinstance(raw, dict) or not raw.get("id") or not raw.get("title"):
            raise QueueError("Each prospect needs id and title")
        item = dict(raw)
        allowed = bool(item.get("contact_after_launch")) and launch_enabled
        item["contact_allowed_now"] = allowed
        item["triage_score"] = score(item)
        if contactable_only and not allowed:
            continue
        ranked.append(item)

    return sorted(
        ranked,
        key=lambda x: (-x["triage_score"], x.get("channel", ""), x["title"]),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("queue", type=Path)
    parser.add_argument("--contactable-only", action="store_true")
    args = parser.parse_args()

    try:
        doc = json.loads(args.queue.read_text(encoding="utf-8"))
        rows = rank_queue(doc, contactable_only=args.contactable_only)
    except (OSError, json.JSONDecodeError, QueueError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2

    print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
