# Specialist Pack Acceptance Verification

Updated: 2026-09-25

Every specialist mode has concrete business-level synthetic acceptance tests.

PCFlows now verifies the specialist pack as a whole, not only individual static findings.

Examples:

## Lead Flow Reliability
All required:
- duplicate lead replay;
- near-simultaneous routing race;
- downstream failure visibility/recovery;
- follow-up stop after reply/booking/human handoff.

## Invoice & Payment Sync
All required:
- duplicate invoice replay;
- partial-payment behavior;
- stable customer matching;
- half-failure reconciliation.

## AI Workflow Guardrails
All required:
- malformed output rejection/quarantine;
- ambiguous/low-confidence review path;
- human-takeover freeze;
- duplicate effect replay.

## Client Onboarding Reliability
All required:
- duplicate setup replay;
- partial onboarding failure;
- required-step skip visibility;
- human handoff boundary.

## Status

- missing/failed test -> open;
- all tests pass only from customer/sanitized evidence -> evidence_supported;
- all tests pass through connected PCFlows-observed synthetic runs -> verified_fixed.

This prevents a customer-facing specialist problem from being declared solved when one of its agreed business acceptance tests still fails.
