# Pilot Launch Gates

Updated: 2026-09-25

## Gate A — product usefulness

- [x] Static Make blueprint parser exists.
- [x] Nested routes/error paths supported.
- [x] Retry/idempotency checks exist.
- [x] Skip/Ignore, Resume, Commit and Rollback/autocommit reliability semantics are reviewed.
- [x] Concurrency, incomplete-execution, data-loss and observability checks exist.
- [x] Higher-consequence rules are mapped to official Make documentation in `RULE_EVIDENCE.md`.
- [x] Synthetic scenario produces meaningful findings.
- [x] Deterministic paid-report builder exists.
- [x] Paid report adds prevent/detect/recover guidance, verification steps and Make references where available.
- [x] Static-analysis limitations are explicit.

## Gate B — privacy / input safety

- [x] Free browser core uses no network calls.
- [x] No production Make token required.
- [x] Secret-like literal detection exists.
- [x] Paid report does not echo arbitrary mapper values.
- [x] Context is allowlisted/bounded.
- [x] Intake schema explicitly excludes arbitrary extra fields.
- [x] Public GitHub Pages deployment activated.
- [x] Paid fulfillment hard-stops on a possible-secret finding.
- [x] Delivery ZIP deliberately excludes the customer's raw blueprint.

## Gate C — commercial evidence

- [x] Demand observed on multiple independent sites.
- [x] Direct generic-linter competitor identified.
- [x] Positioning narrowed away from commodity linting.
- [x] Low-price and higher-value service benchmarks observed.
- [x] Fixed pilot offers defined.
- [ ] First genuine external willingness-to-pay event.
- [ ] First payment-provider-verified external payment.
- [ ] Repeat payment from an independent second customer.

## Gate D — channel compliance

- [x] Make Community rules checked; autonomous posting disabled.
- [x] Upwork off-platform/circumvention rule checked.
- [x] Fiverr off-platform rule checked.
- [x] Contra bulk/systematic outreach restrictions checked.
- [x] Human-realistic pace codified.
- [x] Multi-channel requirement codified.
- [ ] Legitimate marketplace profiles/KYC available where a marketplace is later used.

Marketplace accounts are not required for the initial direct PCFlows pilot.

## Gate E — money

- [x] EUR 0 owner-capital default encoded.
- [x] EUR 500 owner reserve ceiling encoded.
- [x] Strict provider-verified ledger exists.
- [x] Owner/test/pending/refunded target exclusions tested.
- [x] Reinvestment/expenses/refunds/net result separated.
- [x] Stripe account is connected and live-capable.
- [x] EUR 149 Stripe product/one-time price/Payment Link exist.
- [x] PaymentIntent/Refund normalization is implemented against Stripe's real object schema.
- [x] Dry-run provider reconciliation exists and preserves the append-only journal.
- [x] Reconciliation refuses untrusted snapshots, ignores non-final refunds and hard-stops on conflicts.
- [x] Checkout is deliberately disabled during the Belgian registration pause.
- [ ] Belgian enterprise number received and verified.
- [ ] VAT identification / small-enterprise regime completed as legally available before paid launch.

## Gate F — operating autonomy

- [x] Free scan is self-service.
- [x] Local non-sensitive intake generator is self-service.
- [x] Paid report generation is deterministic.
- [x] Paid-audit fit/qualification routing is deterministic.
- [x] AI-assisted review has a privacy-bounded packet and explicit non-invention rules.
- [x] Paid delivery bundle generation is deterministic.
- [x] Included re-scan has deterministic resolved/remaining/new comparison logic.
- [x] Stripe Checkout Session ID is the stable order/fulfillment reference.
- [x] Post-payment redirect and email handoff are prepared without a custom backend.
- [x] Qualification fields are structured.
- [x] Checkout is prepared to collect scenario name, buying-as classification and billing address.
- [x] Support scope is bounded in the pilot definition.
- [x] Revenue measurement logic is deterministic.
- [ ] Checkout -> intake -> delivery is live for real paid customers (checkout intentionally paused pending registration).
- [x] Included re-scan tooling exists and is designed to remain static-evidence-only.
- [ ] Included re-scan lifecycle has been exercised with a real customer.
- [ ] Real support burden measured from pilot customers.

## Validation state

- Last full local Northstar gate before the latest hardening: 31 Python tests PASS + browser scanner regression/privacy PASS.
- Eight additional targeted regression tests were added for fulfillment, Make error-handler semantics and report evidence.
- New fulfillment logic was independently exercised in an isolated test harness (3/3 PASS).
- Five Stripe reconciliation regression tests were independently exercised after implementation (5/5 PASS).
- Existing public repository GitHub Action remains green, but it tests the pre-existing public n8n scanner rather than the isolated Northstar suite.

Do not misrepresent the root CI result as Northstar test coverage.

## Current decision

**Continue EUR 0 technical/launch preparation. Do not inject additional owner capital.**

## Registration pause

As of 2026-09-25:
- Xerius self-employed affiliation: approved;
- Belgian enterprise number: still in processing;
- planned start date: 2026-10-01;
- VAT activation/small-enterprise route: not yet completed.

The live Stripe Payment Link remains inactive until the registration/tax gate is complete.

During the pause, Northstar may continue only useful EUR 0 work. Major safe technical launch preparation is now complete; avoid speculative feature expansion until the enterprise/VAT details or real customer evidence create a concrete need.


## Package ladder readiness
- [x] PCFlows is the sole public/trade brand; Northstar remains internal.
- [x] EUR0 Reliability Preflight exists.
- [x] EUR79 Focused Risk Check renderer exists.
- [x] EUR149 Data Integrity Audit exists.
- [x] Lead Flow / Invoice & Payment / AI Guardrails specialist modes exist inside the EUR149 audit.
- [x] EUR399 Portfolio / Release QA supports up to three scenarios.
- [x] Combined Portfolio remediation re-scan exists.
- [x] Public Services & Pricing page and local service chooser exist.
- [x] Site source QA passes after package redesign.
- [x] Inactive Stripe products/prices for EUR79 and EUR399 created; no public payment links yet.
- [ ] Package-specific Payment Links configured/verified and checkout buttons activated only after Belgian enterprise/VAT gate.


## Fix-verification readiness
- [x] Every current deterministic rule is registered in a central rule list.
- [x] Every rule has a verification specification.
- [x] Every rule has a synthetic static before/after regression fixture.
- [x] Re-scan language says statically cleared / remaining / new, not simply fixed.
- [x] Customer claim guard blocks unsupported absolute success/fix claims in paid reports.
- [x] Remediation proof report distinguishes static clearance, supporting evidence and independently verified fixed.
- [x] Public verification page explains the proof levels before purchase.
- [ ] Direct connected Make.com synthetic test path available.
- [ ] Runtime-dependent issues independently verified end-to-end in that connected test path.
- [ ] Done-for-you repair/fix package remains NOT launched until the two gates above pass.

Commercial rule: the current packages sell audit, remediation guidance, verification plans and re-scan. Do not market a guaranteed live fix.
