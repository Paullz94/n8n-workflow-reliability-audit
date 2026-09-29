# PCFlows Launch Gate

This document defines the remaining conditions before paid sales can be activated.

## Commercial start

PCFlows is B2B-only at launch. Paid service, payment acceptance and invoicing begin **no earlier than 2026-10-01**.

Clearly labeled pre-launch B2B acquisition may run before that date, without implying paid fulfillment is already available.

## Completed owner prerequisites

1. Belgian KBO registration — complete; enterprise number **1043.055.054**.
2. Social-insurance/tax readiness — owner confirmed complete.
3. VAT status — owner confirmed in order. The numeric VAT identifier remains private until an actual customer needs it. VAT is not a blocker.

## Remaining public seller publication gate

The following values require deliberate owner-approved publication rather than inference from connected accounts:
- legal seller name;
- registered business address;
- professional phone/contact number if used as a required public field.

Already known for public use:
- trade name: PCFlows;
- enterprise number: 1043.055.054;
- professional email: pcmotionstudios@gmail.com;
- non-sensitive VAT status statement.

Do not automatically publish a private home address, personal phone number or numeric VAT identifier.

## Stripe / checkout state

Canonical staged offers:
- Focused Risk Check — EUR 79;
- Data Integrity Audit — EUR 149;
- Portfolio / Release QA — EUR 399.

The canonical products/prices are active in live-mode Stripe. Their Payment Links are deliberately **inactive** before launch.

The superseded EUR 249 n8n Reliability Audit and EUR 890 n8n Reliability Retrofit products/prices are inactive.

The public repository contains the correct staged Payment Link URLs, but checkoutEnabled remains false, site.js enforces the 2026-10-01 start date, seller identity must be complete, and Stripe links must be activated before public checkout is switched on.

## Activation procedure

On or after 2026-10-01, and only after the public seller identity gate is complete:

1. verify Stripe/KYC shows no genuine owner action;
2. activate all three canonical Payment Links;
3. set checkoutEnabled=true in launch-config.js;
4. run public CI;
5. verify the legal page and all three checkout-to-intake redirects;
6. verify the first real payment is external, settled, non-test and non-refunded;
7. reconcile the payment before fulfillment.

If a genuine settled external payment somehow appears before 2026-10-01, flag it for review instead of treating it as a normal order.

## Commercial validation

EUR 1,000 verified gross revenue is the first minimum validation milestone, not a stop condition. Continue acquiring and serving customers after the milestone.

Only settled external-customer revenue counts. Tests, owner-funded transactions, pending/failed payments and refunds do not count.
