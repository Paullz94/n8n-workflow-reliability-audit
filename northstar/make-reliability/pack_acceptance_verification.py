#!/usr/bin/env python3
"""Verify specialist-pack acceptance tests from explicit evidence."""
from __future__ import annotations

from typing import Any

import vertical_packs


class PackVerificationError(ValueError):
    pass


TRUSTED_SOURCES={"connected_test_run"}
SUPPORTING_SOURCES={"customer_test_record","sanitized_execution_evidence"}


def required_test_ids(pack_id:str)->list[str]:
    pack=vertical_packs.get_pack(pack_id)
    return [item["id"] for item in pack.acceptance_tests]


def verify_pack_acceptance(
    pack_id:str,
    evidence_items:list[dict[str,Any]],
)->dict[str,Any]:
    required=required_test_ids(pack_id)
    by_id={}
    for item in evidence_items:
        if not isinstance(item,dict):
            continue
        tid=str(item.get("test_id") or "").strip()
        if tid:
            by_id[tid]=item

    rows=[]
    for tid in required:
        evidence=by_id.get(tid)
        if not evidence:
            rows.append({
                "test_id":tid,
                "status":"missing",
                "independently_verified":False,
            })
            continue
        source=str(evidence.get("source") or "").strip()
        passed=evidence.get("passed") is True
        if not passed:
            status="failed"
        elif source in TRUSTED_SOURCES:
            status="passed_connected"
        elif source in SUPPORTING_SOURCES:
            status="passed_supporting"
        else:
            status="untrusted_source"
        rows.append({
            "test_id":tid,
            "status":status,
            "independently_verified":status=="passed_connected",
            "source":source or None,
        })

    return {
        "pack_id":pack_id,
        "required_count":len(required),
        "results":rows,
        "all_tests_passed":all(r["status"] in {"passed_connected","passed_supporting"} for r in rows),
        "all_tests_independently_verified":all(r["status"]=="passed_connected" for r in rows),
        "customer_status":(
            "verified_fixed" if all(r["status"]=="passed_connected" for r in rows)
            else "evidence_supported" if all(r["status"] in {"passed_connected","passed_supporting"} for r in rows)
            else "open"
        ),
    }
