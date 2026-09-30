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
    *,
    trusted_connected_evidence:bool=False,
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
        assertions=evidence.get("assertions")
        assertions_ok=isinstance(assertions,dict) and bool(assertions) and all(value is True for value in assertions.values())
        execution_ids=evidence.get("execution_ids")
        connected_ok=(
            trusted_connected_evidence is True
            and source in TRUSTED_SOURCES
            and evidence.get("provider")=="make"
            and evidence.get("observed_by_pcflows") is True
            and isinstance(execution_ids,list)
            and bool([x for x in execution_ids if x])
            and assertions_ok
        )
        passed=evidence.get("passed") is True
        if not passed:
            status="failed"
        elif connected_ok:
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
