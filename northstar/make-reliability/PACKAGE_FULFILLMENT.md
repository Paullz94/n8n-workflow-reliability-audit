# Unified Package Fulfillment

Updated: 2026-09-25

`package_fulfillment.py` is the package-aware paid delivery entry point.

It requires a provider-verified Stripe Checkout Session snapshot that passes `order_contract.py`.

## EUR79 Focused Risk Check

Inputs:
- paid order snapshot with `pcflows_package=focused_risk_check`;
- one sanitized blueprint;
- one safe context file;
- one selected focus: duplicates, silent_skips, recovery or ordering.

Output:
- focused report;
- findings JSON;
- context-used JSON;
- manifest;
- ZIP.

No raw blueprint in the ZIP.
No included re-scan.

## EUR149 Data Integrity Audit

Routes through the established `fulfill_order.py` pipeline.

Automatic specialist selection remains:
- Lead Flow Reliability;
- Invoice & Payment Sync;
- AI Workflow Guardrails;
- generic when context is ambiguous.

One re-scan remains included.

## EUR399 Portfolio / Release QA

Inputs:
- paid order snapshot with exact EUR399 package metadata;
- 1 to 3 scenario blueprint/context pairs.

Output:
- combined portfolio/release report;
- aggregate summary;
- manifest;
- ZIP.

Internal AI-review packets are generated per scenario but excluded from the customer ZIP.
Raw blueprints are excluded.
One combined before/after re-scan round is included via `portfolio_rescan.py`.

## Hard stops

- wrong package/amount;
- non-EUR;
- unpaid/unverified/test/owner transaction;
- secret-like input in any supplied scenario;
- missing required context;
- nonempty output directory.

The package contract is intentionally stricter than customer-facing marketing copy.
