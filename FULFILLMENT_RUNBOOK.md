# PCFlows Fulfillment Runbook

This runbook applies only to paid B2B orders accepted on or after 2026-10-01.

## 1. Payment event

Source of truth: Stripe.

A customer is considered paid only when Stripe shows a successful settled external-customer payment for the relevant PCFlows offer.

Before fulfillment, verify the payment is live-mode, external rather than owner/test, successful and settled, not pending, and not refunded or disputed.

If a genuine settled external payment somehow appears before 2026-10-01, stop normal fulfillment and flag it for review.

## 2. Canonical packages

### Focused Risk Check — EUR 79
- one sanitized n8n workflow JSON export;
- one agreed reliability risk area;
- no included re-scan.

### Data Integrity Audit — EUR 149
- one sanitized n8n workflow JSON export;
- broader reliability/data-integrity review;
- one asynchronous re-scan after remediation.

### Portfolio / Release QA — EUR 399
- up to three related sanitized n8n workflow JSON exports;
- combined release-risk/reliability view;
- one combined re-scan round.

## 3. Intake

Stripe redirects the buyer to intake.html carrying offer and session_id.

Required metadata: company, business outcome, connected systems by name, symptom/risk, n8n version + hosting type, approximate node count per workflow, and acceptance condition.

Reject or pause intake when secrets are present, unnecessary personal/customer data is present, files exceed the purchased package, or exports are not valid n8n workflow objects.

## 4. Static delivery pack

For each workflow export in scope, run:

    python package_audit.py customer-workflow.json --output-dir delivery --order-ref CHECKOUT_SESSION_ID

Expected output includes 01-audit-report.md, 02-audit-report.json, 03-client-summary.md, 04-synthetic-verification-plan.md and MANIFEST.json.

For Portfolio / Release QA, keep per-workflow packs separate and add a combined manual release-risk summary; do not overwrite input hashes.

## 5. Manual review gate

The automated package is not the final paid deliverable by itself. Inspect critical/high findings, remove obvious heuristic false positives, add customer-specific context, ensure no secrets appear, keep recommendations within purchased scope, and confirm claims are evidence-backed.

## 6. Delivery and re-scan

Send the final package to the paying business contact through the Inbox Operator workflow.

Purchased re-scan allowance:
- Focused Risk Check: none;
- Data Integrity Audit: one;
- Portfolio / Release QA: one combined round.

Preserve original and re-scan hashes separately.

## 7. Completion

Mark an engagement complete only when deliverables were sent, the purchased re-scan allowance is completed or explicitly unused, no customer secrets remain in public repositories, and Stripe payment/refund/dispute state is reconciled.

EUR 1,000 verified gross is the first minimum validation milestone, not a stop condition.
