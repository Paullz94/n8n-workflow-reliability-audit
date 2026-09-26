# Paid Audit Fulfillment Runbook

Updated: 2026-09-25

Purpose: keep the EUR 149 pilot bounded and repeatable while preserving privacy.

## Customer path

1. Customer pays through the PCFlows Stripe Payment Link.
2. Stripe redirects to `thanks.html?session_id={CHECKOUT_SESSION_ID}`.
3. The page gives the customer a pre-filled support-email subject containing the Stripe Checkout Session ID.
4. Customer attaches:
   - one sanitized Make.com blueprint JSON;
   - one PCFlows intake JSON generated locally at `intake.html`.
5. Never request production credentials, passwords, API keys, private webhook secrets or raw customer records.

## Operator fulfillment

Store customer files outside the public repository.

Run:

```bash
python fulfill_order.py customer-blueprint.json \
  --context customer-intake.json \
  --order-ref cs_... \
  --out-dir delivery/cs_...
```

The command:
- validates the Stripe-style order reference;
- allowlists intake/context fields;
- runs the deterministic scanner;
- **hard-stops if a possible secret-like literal is detected**;
- generates the paid Data Integrity Audit;
- generates machine-readable findings;
- generates an integrity manifest with SHA-256 input/output hashes;
- creates `pcflows-audit-delivery.zip`;
- deliberately excludes the raw blueprint from the delivery ZIP.

## Pre-send QA

Before delivery:
- verify the order exists and is paid in Stripe;
- verify it is not an owner/test payment;
- verify the scenario name matches the customer's order/intake;
- inspect the high/critical findings for obvious false positives;
- confirm no secret warning exists;
- send only the generated delivery ZIP, not the customer's raw blueprint.

## Re-scan entitlement

The EUR 149 pilot includes one asynchronous re-scan after remediation.

Use the same Stripe Checkout Session ID as the stable order reference. Do not create a second revenue event for the included re-scan.

## Repository privacy rule

Never commit:
- customer blueprints;
- customer intake files;
- customer reports;
- customer email addresses;
- Stripe Checkout Session IDs tied to real customers.

Only product code, synthetic fixtures and aggregate/non-identifying product learnings belong in GitHub.
