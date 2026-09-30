#!/usr/bin/env python3
"""Recommend the smallest suitable PCFlows package from bounded inputs."""
from __future__ import annotations

from typing import Any


VALID_FOCUSES={"duplicates","silent_skips","recovery","ordering"}


def recommend_package(
    *,
    scenario_count:int=1,
    qualification_route:str|None=None,
    requested_scope:str|None=None,
    requested_focus:str|None=None,
) -> dict[str,Any]:
    if scenario_count < 1:
        raise ValueError("scenario_count must be >= 1")
    if scenario_count > 3:
        return {
            "package_id":None,
            "route":"out_of_catalog",
            "reason":"The fixed Portfolio / Release QA catalog supports at most 3 scenarios.",
        }

    if qualification_route=="free_preflight_sufficient" or requested_scope=="explore":
        return {
            "package_id":"preflight_free",
            "price_eur":0,
            "reason":"The free local preflight is the smallest useful scope.",
        }

    if scenario_count>=2 or requested_scope=="release":
        return {
            "package_id":"portfolio_release_qa",
            "price_eur":399,
            "reason":"Multiple scenarios or release/handoff context benefits from one combined portfolio view.",
        }

    if requested_scope=="focused" and requested_focus in VALID_FOCUSES:
        return {
            "package_id":"focused_risk_check",
            "price_eur":79,
            "reason":"One explicit risk focus does not require the full cross-category audit.",
        }

    return {
        "package_id":"data_integrity_audit",
        "price_eur":149,
        "reason":"One important scenario needs the full reliability/data-integrity scope.",
    }
