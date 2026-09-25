# Pilot FAQ

Updated: 2026-09-25

## Does Northstar need access to my Make account?

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

## What is the pilot price?

The primary pilot hypothesis is EUR 149 for one sanitized blueprint, bounded interpretation, up to two redacted/synthetic examples and one asynchronous re-scan.

This is a test offer, not evidence of existing customers or revenue.

## Are refunds counted toward the EUR 1,000 Northstar target?

No. The internal target policy is stricter: any completed refund disqualifies that entire payment from target-eligible gross revenue.

## Can you implement the whole automation for me?

Not in the core audit offer. Open-ended implementation would make the model operator-heavy. Separate implementation work is intentionally outside the initial Northstar end-state.

## Can I send production credentials so you can check everything?

No. The pilot is designed to avoid production credentials.

## Is this affiliated with Make?

No. Northstar is an independent reliability-audit project and is not presented as an official Make product or certification.
