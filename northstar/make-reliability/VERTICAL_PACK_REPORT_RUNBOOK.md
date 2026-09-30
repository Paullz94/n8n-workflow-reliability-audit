# Vertical Pack Report Runbook

Updated: 2026-09-25

The same deterministic PCFlows core can now render four buyer-specific audit layers.

## Commands

Lead flow:

python build_pack_report.py lead_flow examples/vertical/lead-flow-blueprint.json --context examples/vertical/lead-flow-context.json --out lead-flow-report.md

Invoice/payment:

python build_pack_report.py invoice_payment examples/vertical/invoice-payment-blueprint.json --context examples/vertical/invoice-payment-context.json --out invoice-payment-report.md

AI guardrails:

python build_pack_report.py ai_guardrails examples/vertical/ai-guardrails-blueprint.json --context examples/vertical/ai-guardrails-context.json --out ai-guardrails-report.md

Client onboarding:

python build_pack_report.py client_onboarding <sanitized-blueprint.json> --context <safe-context.json> --out client-onboarding-report.md

## Design rule

A pack may:
- change buyer wording;
- prioritize existing deterministic rules;
- add synthetic acceptance tests;
- add domain-specific context questions.

A pack may not:
- invent live incidents;
- claim a static finding proves a defect;
- request production credentials;
- silently expand into implementation;
- use domain language to imply accounting/security/compliance certification.

## Autonomy value

Pack-specific reports make customer delivery more automatable:
- qualification chooses a pack;
- the same scanner produces evidence;
- the pack supplies the acceptance tests;
- the AI-review packet can explain the result within the deterministic boundary;
- fulfillment stays identical;
- one re-scan remains identical.

This avoids a manual consulting workflow per customer.
