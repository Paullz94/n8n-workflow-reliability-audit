# Stripe Package Checkout Specification

Updated: 2026-09-25

This is the canonical launch-time checkout configuration for the fixed PCFlows package ladder.

## Why EUR79/EUR399 links are not pre-created

Stripe's Payment Link create endpoint does not expose an `active=false` creation field in the current API schema. A newly created link is therefore not guaranteed to be born inactive.

During the Belgian registration pause, PCFlows will not create a checkout that could be live even briefly.

So:
- EUR149 existing link stays inactive;
- EUR79/EUR399 products/prices are prepared;
- EUR79/EUR399 Payment Links are created only after the legal launch gate is complete;
- immediately verify their package metadata/fields before publishing them on the site.

## Global checkout requirements

Every paid package:
- EUR only;
- billing address required;
- tax-ID collection enabled;
- Buying as field required: individual/consumer vs business/professional;
- customer is reminded not to submit secrets/credentials;
- post-payment redirect includes Checkout Session ID;
- package metadata is copied to both Checkout Session/PaymentIntent paths where supported.

## EUR79 Focused Risk Check

Price:
`price_1UJfIULEUPyOUtb0PVbLXkFt`

Required custom fields:
- Scenario name;
- Risk focus:
  - duplicate effects / idempotency;
  - silent skips / missing work;
  - failure recovery;
  - concurrency / ordering;
- Buying as.

Required metadata:
`pcflows_package=focused_risk_check`

## EUR149 Data Integrity Audit

Price:
`price_1UJYXlLEUPyOUtb0yovnfhH0`

Prepared Payment Link:
`plink_1UJYXyLEUPyOUtb0elSom4yX`

Current state:
**inactive**

Required custom fields:
- Scenario name;
- Buying as.

Required metadata:
`pcflows_package=data_integrity_audit`

## EUR399 Portfolio / Release QA

Price:
`price_1UJfIWLEUPyOUtb0EfhLDC8P`

Required custom fields:
- Portfolio / release name;
- Scenario count: 1 / 2 / 3;
- Buying as.

Required metadata:
`pcflows_package=portfolio_release_qa`

## Activation order

After KBO/VAT gate:
1. verify official Stripe business identity;
2. create EUR79 and EUR399 links;
3. configure exact custom fields/metadata;
4. retrieve each link and verify configuration;
5. execute one owner/test checkout per relevant path only if needed, mark as test/owner and exclude from revenue;
6. deactivate or refund test transaction as applicable;
7. reconcile test evidence;
8. expose public website checkout buttons;
9. re-check live pages once.

The strict `order_contract.py` and `stripe_checkout_adapter.py` remain the fulfillment gate even after public activation.
