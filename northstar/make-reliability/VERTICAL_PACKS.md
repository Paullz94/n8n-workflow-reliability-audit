# Problem-Specific Audit Packs

Updated: 2026-09-25

PCFlows now has three internally implemented demand packs layered on the same deterministic reliability engine.

## 1. Lead Flow Reliability

Plain customer problem:
> Leads disappear, duplicate, route to the wrong salesperson, or keep receiving automation after they replied/booked.

The pack adds:
- duplicate replay acceptance test;
- near-simultaneous routing/race test;
- downstream CRM/SMS/email failure test;
- reply/booking/human-takeover stop test;
- lead-specific context prompts.

## 2. Invoice & Payment Sync

Plain customer problem:
> CRM, invoicing and payment tools disagree, create duplicate invoices, match the wrong customer or close a deal after only a partial payment.

The pack adds:
- duplicate invoice replay test;
- partial-payment test;
- stable customer matching collision test;
- cross-system half-failure/reconciliation test;
- finance source-of-truth context prompts.

## 3. AI Workflow Guardrails

Plain customer problem:
> AI returns malformed/uncertain/wrong output, but the automation still writes to CRM, finance, email or customer-facing systems.

The pack adds:
- malformed/null/wrong-type output test;
- ambiguous/low-confidence review test;
- human-handoff freeze test;
- duplicate external effect after replay test;
- AI decision/approval boundary context prompts.

## Architecture

These packs do not fork the product.

They reuse:
- audit_make.py
- report_builder.py
- secret gate
- AI review packet
- fulfillment pipeline
- qualification
- Stripe/payment ledger
- before/after re-scan

vertical_packs.py adds only:
- buyer-specific priority ordering;
- customer-readable problem framing;
- pack-specific context prompts;
- synthetic acceptance tests.

This preserves autonomy and keeps support/fulfillment deterministic.

## Public launch gate

The packs are internally ready for further testing, but remain non-public paid products until:
- Belgian enterprise/VAT activation is complete;
- each synthetic fixture/report passes the validation suite;
- the main EUR149 offer can be purchased legally;
- at least one channel can be operated autonomously or through a connected integration.


## 4. Client Onboarding Reliability

Plain customer problem:
> A new customer is created in some systems but missing from others, gets duplicate welcome/setup actions, or becomes stuck halfway through onboarding.

The pack adds:
- duplicate client/project/folder/task replay test;
- partial-onboarding failure test;
- required-step silent-skip test;
- automation-to-human handoff test;
- onboarding-completion context prompts.
