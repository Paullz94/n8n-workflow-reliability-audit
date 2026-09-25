#!/usr/bin/env python3
"""Execute a bounded PCFlows repair verification cycle in an allowlisted Make sandbox.

The runner never deploys to production. It:
1. validates the revised blueprint locally;
2. backs up the current sandbox blueprint;
3. applies the revised blueprint;
4. executes explicit synthetic acceptance tests;
5. rolls back automatically if any test fails or errors;
6. emits trusted connected-test evidence only when the relevant assertions pass.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import audit_make
import make_runtime_client
import runtime_test_contract


class SandboxRepairError(RuntimeError):
    pass


EVALUATORS: dict[str, Callable[..., dict[str, bool]]] = {
    "duplicate_replay": runtime_test_contract.assert_duplicate_replay,
    "failure_recovery": runtime_test_contract.assert_failure_recovery,
    "human_handoff": runtime_test_contract.assert_human_handoff,
    "partial_payment": runtime_test_contract.assert_partial_payment,
    "invalid_ai_output": runtime_test_contract.assert_invalid_ai_output,
    "onboarding_resources": runtime_test_contract.assert_required_onboarding_resources,
}


def _canonical_sha256(value: dict[str, Any]) -> str:
    payload=json.dumps(value,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _contains_secret_like(value: Any) -> bool:
    if isinstance(value,str):
        return any(pattern.search(value) for pattern in audit_make.SECRET_PATTERNS)
    if isinstance(value,dict):
        return any(_contains_secret_like(v) for v in value.values())
    if isinstance(value,list):
        return any(_contains_secret_like(v) for v in value)
    return False


def _extract_result(run_response: dict[str, Any]) -> dict[str, Any]:
    """Extract only an explicit structured proof object from a responsive run."""
    for key in ("output","outputs","result"):
        value=run_response.get(key)
        if isinstance(value,dict):
            return runtime_test_contract.sanitize_result(value)
        if isinstance(value,list) and len(value)==1 and isinstance(value[0],dict):
            return runtime_test_contract.sanitize_result(value[0])
    raise SandboxRepairError(
        "responsive Make run did not return one structured proof object in output/outputs/result"
    )


def _assert_all_true(assertions: dict[str, bool], test_id: str) -> None:
    failed=[key for key,value in assertions.items() if value is not True]
    if failed:
        raise SandboxRepairError(
            f"acceptance test {test_id} failed assertions: {', '.join(sorted(failed))}"
        )


def _run_test(
    client: make_runtime_client.MakeRuntimeClient,
    scenario_id: int,
    spec: dict[str, Any],
) -> dict[str, Any]:
    test_id=str(spec.get("test_id") or "").strip()
    evaluator_name=str(spec.get("evaluator") or "").strip()
    if not test_id:
        raise SandboxRepairError("every test requires test_id")
    evaluator=EVALUATORS.get(evaluator_name)
    if evaluator is None:
        raise SandboxRepairError(f"{test_id}: unsupported evaluator {evaluator_name!r}")

    input_data=spec.get("input")
    if input_data is not None and not isinstance(input_data,dict):
        raise SandboxRepairError(f"{test_id}: input must be an object")
    if _contains_secret_like(input_data or {}):
        raise SandboxRepairError(f"{test_id}: secret-like literal detected in synthetic input")

    if evaluator_name=="duplicate_replay":
        first=client.run_scenario(scenario_id,data=input_data or {},responsive=True)
        second=client.run_scenario(scenario_id,data=input_data or {},responsive=True)
        proof1=_extract_result(first)
        proof2=_extract_result(second)
        assertions=evaluator(proof1,proof2)
        execution_ids=[first.get("executionId"),second.get("executionId")]
        sanitized_outputs=[proof1,proof2]
    else:
        response=client.run_scenario(scenario_id,data=input_data or {},responsive=True)
        proof=_extract_result(response)
        assertions=evaluator(proof)
        execution_ids=[response.get("executionId")]
        sanitized_outputs=[proof]

    _assert_all_true(assertions,test_id)
    return {
        "test_id":test_id,
        "evaluator":evaluator_name,
        "source":"connected_test_run",
        "passed":True,
        "assertions":assertions,
        "execution_ids":[x for x in execution_ids if x],
        "sanitized_outputs":sanitized_outputs,
    }


def run_sandbox_repair(
    *,
    client: make_runtime_client.MakeRuntimeClient,
    scenario_id: int,
    revised_blueprint: dict[str, Any],
    test_plan: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(revised_blueprint,dict):
        raise SandboxRepairError("revised_blueprint must be an object")
    if not test_plan:
        raise SandboxRepairError("at least one acceptance test is required")

    revised_findings=audit_make.scan_blueprint(revised_blueprint)
    if any(f.rule=="possible-secret-in-blueprint" for f in revised_findings):
        raise SandboxRepairError("revised blueprint contains possible secret-like input")

    backup=None
    rollback_attempted=False
    try:
        backup=client.update_sandbox_blueprint(scenario_id,revised_blueprint)
        original=backup.get("original_blueprint")
        if not isinstance(original,dict):
            raise SandboxRepairError("sandbox update did not return the original blueprint backup")

        deployed=client.get_blueprint(scenario_id)
        deployed_findings=audit_make.scan_blueprint(deployed)
        if any(f.rule=="possible-secret-in-blueprint" for f in deployed_findings):
            raise SandboxRepairError("deployed sandbox blueprint contains possible secret-like input")

        tests=[]
        for spec in test_plan:
            tests.append(_run_test(client,scenario_id,spec))

        return {
            "scenario_id":int(scenario_id),
            "status":"verified_in_sandbox",
            "all_tests_passed":True,
            "original_sha256":backup.get("original_sha256") or _canonical_sha256(original),
            "requested_revised_sha256":_canonical_sha256(revised_blueprint),
            "deployed_sha256":_canonical_sha256(deployed),
            "tests":tests,
            "rollback_performed":False,
            "customer_claim":"All supplied acceptance tests passed in the connected allowlisted Make sandbox. Production deployment remains a separate gated step.",
        }
    except Exception as exc:
        rollback_error=None
        if isinstance(backup,dict) and isinstance(backup.get("original_blueprint"),dict):
            rollback_attempted=True
            try:
                client.rollback_sandbox_blueprint(
                    scenario_id,
                    backup["original_blueprint"],
                )
            except Exception as rollback_exc:  # deliberately surface both failures
                rollback_error=str(rollback_exc)
        message=f"sandbox repair verification failed: {exc}"
        if rollback_error:
            message+=f"; automatic rollback also failed: {rollback_error}"
        elif rollback_attempted:
            message+="; original sandbox blueprint was restored"
        raise SandboxRepairError(message) from exc


def load_plan(path: Path) -> list[dict[str, Any]]:
    try:
        value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:
        raise SandboxRepairError(f"test plan is not valid JSON: {exc}") from exc
    if not isinstance(value,list) or not all(isinstance(x,dict) for x in value):
        raise SandboxRepairError("test plan root must be an array of objects")
    return value
