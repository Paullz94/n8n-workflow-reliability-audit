# Project Northstar Ledger — Make Reliability & Data Integrity

Updated: 2026-09-25  
Status: technical pilot package / EUR 0 owner capital  
Branch: `northstar/make-reliability-20260925`

This directory is intentionally isolated from the pre-existing n8n product files.

## North-star target

Reach **EUR 1,000 payment-provider-verified gross revenue from real external customers** while keeping:
- owner reserve: EUR 500 uninjected;
- owner capital injected: EUR 0 by default;
- business-generated cash, reinvestment, expenses, refunds, net revenue and operating result separately tracked.

Owner, test, pending, unverified, fictitious and refunded payments do not count toward the target.

See:
- `../NORTHSTAR_GOAL.md`
- `LEDGER_POLICY.md`
- `ledger_engine.py`

## Product direction

Northstar is **not** positioned as a generic Make blueprint linter.

The wedge is a privacy-first **reliability and data-integrity** review focused on:
- duplicate writes and retry/idempotency;
- concurrent-write/ordering risk;
- silent skips caused by filters/routes;
- missing failure/recovery paths;
- incomplete-execution/data-loss configuration;
- privacy-safe observability;
- remediation and verification order.

See `POSITIONING.md`.

## Free asset — Reliability Preflight

The free core can run locally:
- Python CLI: `audit_make.py`
- browser client: `web/index.html`
- browser scan has no external JavaScript dependency and makes no network request;
- blueprint processing stays in the browser for the core preflight;
- no Make token or production credentials are required.

Example:

```bash
python audit_make.py examples/synthetic-order-intake.json \
  --json-out findings.json \
  --md-out preflight.md
```

## Paid pilot automation

`report_builder.py` turns scanner findings plus an allowlisted, non-sensitive context object into a deterministic Data Integrity Audit.

Example:

```bash
python report_builder.py \
  examples/synthetic-order-intake.json \
  --context examples/synthetic-context.json \
  --out paid-audit.md
```

The builder:
- preserves severity ordering;
- categorizes work into prevent / detect / recover;
- adds business-impact guidance;
- adds deterministic remediation and verification steps;
- does not copy arbitrary blueprint mapper values into the report;
- accepts only allowlisted context keys.

Synthetic example:
- `examples/synthetic-order-intake.json`
- `examples/synthetic-context.json`
- `examples/synthetic-paid-audit.md`

## Pilot price hypotheses

These are experiments, not booked revenue:

| Offer | Price | Purpose |
|---|---:|---|
| Reliability Preflight+ | EUR 49 | automated single-blueprint report |
| Data Integrity Audit | **EUR 149** | primary WTP pilot, bounded interpretation + one re-scan |
| Small Portfolio Audit | EUR 299 | up to 3 related blueprints; do not launch until EUR 149 tier is bounded |

Seven genuine unrefunded EUR 149 external payments would equal EUR 1,043. This is arithmetic, not a forecast.

See `PILOT.md`.

## Financial verification

`ledger_engine.py` consumes an append-only normalized journal.

Strict invariants include:
- payment-provider verification required;
- only real external EUR payments are target-eligible in the pilot;
- owner/test/pending transactions never count;
- any completed refund disqualifies the entire payment from the EUR 1,000 target;
- owner capital requires explicit Paul approval;
- owner injections above EUR 500 are rejected;
- revenue-funded reinvestment and total expenses remain separate.

Current journal: `ledger_journal.json` (empty).

## Acquisition portfolio

Northstar does not depend on one site.

Current research/distribution portfolio:
- GitHub — directly controlled technical trust asset;
- Make Community — **autonomous research only**, because current rules prohibit AI-generated/automated community content;
- Upwork — high-intent research; future platform-contained proposals only;
- Fiverr — pricing/packaging research; future native Gig only;
- Contra — demand benchmark; no bulk/systematic outreach;
- Zapier ecosystem — adjacent expansion only after Make validation;
- Reddit — research unless current subreddit rules explicitly permit relevant commercial participation.

See:
- `ACQUISITION_CHANNELS.md`
- `CHANNEL_GUARDRAILS.md`
- `VALIDATION_EVIDENCE.md`

## Human-realistic operating rule

Northstar optimizes for durable trust rather than activity volume.

No:
- bulk DMs or scraped mailing;
- duplicate/cross-post blasts;
- multiple accounts or moderation bypass;
- CAPTCHA/rate-limit evasion;
- automation designed to impersonate human activity;
- unrealistic simultaneous launches across many platforms.

Future activity should happen in small, relevant, platform-native increments with time to observe response quality before increasing volume.

## Validation

Run:

```bash
python validate.py
```

Current validated local gate:
- 23 Python unit tests: PASS;
- browser scanner regression/privacy checks: PASS.

The browser test is skipped only when Node.js is unavailable.

## Checkout status

No payment/KYC account has been activated by Northstar.

Current direct-customer candidates:
1. Stripe Payment Links;
2. Payhip;
3. Ko-fi;
4. Gumroad.

Lemon Squeezy is rejected for the current service pilot because its published policy excludes services.

Marketplace-originated leads must use the payment path required by that marketplace; direct checkout must never be used to circumvent marketplace fees/rules.

## Autonomy requirement

The end-state must support:
- acquisition;
- qualification;
- fixed pricing;
- self-service checkout;
- automated delivery;
- bounded support;
- provider-verified measurement;
- iterative rules/product improvement;

without requiring Paul as the daily operator.

The manual pilot may exist only to validate willingness to pay and must shrink as findings become deterministic product logic.

## Stop / pivot gate

Continue safe EUR 0 work while:
- independent buyer signals exist;
- useful static/deterministic analysis is possible;
- compliant acquisition paths exist;
- the product can move toward self-service.

Stop or pivot only on:
- EUR 1,000 verified success;
- a genuine legal/safety/KYC/financial blocker requiring Paul;
- documented strategic failure after real validation.
