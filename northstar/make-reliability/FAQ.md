# Pilot FAQ

Updated: 2026-09-25

## Does PCFlows need access to my Make account?

No for the current blueprint audit. The intended input is a sanitized exported blueprint. Production credentials are out of scope.

## Does the free scanner upload my blueprint?

The current browser core has no network request in its scan path and uses no external JavaScript dependency. The scan runs in the browser.

## What should I remove before sharing a blueprint?

Remove or replace API keys, tokens, passwords, private webhook secrets, personal data and any other confidential literals. The scanner also flags several secret-like patterns as a safety check.

## What does the audit look for?

Current focus:
- missing write error handling;
- automatic retry/idempotency risk;
- mutating HTTP requests;
- filtered writes that may silently skip work;
- concurrency/ordering risk;
- incomplete-execution and data-loss settings;
- privacy/observability trade-offs;
- exported Make designer warnings.

## What does it not prove?

Static analysis cannot prove:
- credentials are valid;
- external services are available;
- runtime data is correct;
- business rules are complete;
- every defect has been found;
- a scenario is legally/compliantly configured.

## Why not just use a generic blueprint linter?

Generic linting is useful and already commoditized. Northstar is deliberately narrower: reliability, recovery and business-data integrity, with remediation/verification ordering.

## What does PCFlows cost?

Current fixed launch ladder:
- EUR0 Reliability Preflight — local static scan;
- EUR79 Focused Risk Check — one selected risk family in one sanitized scenario, no included re-scan;
- EUR149 Data Integrity Audit — full one-scenario reliability/data-integrity review with one re-scan;
- EUR399 Portfolio / Release QA — normally 2–3 related scenarios with a combined release/handoff view and one combined re-scan round.

Lead Flow Reliability, Invoice & Payment Sync, AI Workflow Guardrails and Client Onboarding Reliability are specialist modes inside the EUR149 audit, not separate surcharges.

Prices remain market hypotheses until real external customers buy.

## Are refunds counted toward the EUR 1,000 Northstar target?

No. The internal target policy is stricter: any completed refund disqualifies that entire payment from target-eligible gross revenue.

## Can you implement the whole automation for me?

Not in the core audit offer. Open-ended implementation would make the model operator-heavy. Separate implementation work is intentionally outside the initial Northstar end-state.

## Can I send production credentials so you can check everything?

No. The pilot is designed to avoid production credentials.

## Is this affiliated with Make?

No. PCFlows is an independent technical reliability service and is not presented as an official Make product or certification.
