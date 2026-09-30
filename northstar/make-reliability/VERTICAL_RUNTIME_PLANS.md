# Specialist Runtime Plans

Updated: 2026-09-25

Each PCFlows specialist mode now has a fixed executable synthetic plan whose test IDs exactly match the pack's published acceptance tests.

## Lead Flow
- duplicate replay;
- true two-call concurrent routing race;
- downstream failure/recovery;
- human/reply handoff stop.

## Invoice & Payment
- duplicate invoice replay;
- partial payment;
- stable customer match collision;
- failure after first state-changing write with reconciliation.

## AI Workflow Guardrails
- malformed output rejection;
- ambiguous/low-confidence review route;
- human takeover stop;
- duplicate external effect replay.

## Client Onboarding
- duplicate setup replay;
- partial onboarding failure;
- required-resource completeness;
- human ownership handoff.

All test inputs are explicitly synthetic and labeled `SYN-`.

Every plan is also marked production-safe at the plan level, but that mark is only meaningful after the target workflow has been adapted so these test cases cannot affect real customer records or payments.

The registry hard-stops if a specialist pack adds/removes an acceptance test without the runtime plan being updated.
