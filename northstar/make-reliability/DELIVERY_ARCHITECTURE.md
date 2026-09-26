# Delivery Architecture

Updated: 2026-09-25

## Design objective

Move from a bounded manual WTP pilot to self-service delivery without making Paul the daily operator.

## Stage 0 — current

Input:
- local sanitized Make blueprint JSON.

Processing:
- Python static analyzer;
- deterministic reliability rules;
- JSON and Markdown output;
- no external API calls.

State:
- 11 focused regression tests;
- support for direct blueprints, common blueprint wrappers, nested routes and error handlers.

## Stage 1 — privacy-first free scanner

Target:
- a static browser application or similarly local client that never needs to upload the blueprint for the core scan.

Flow:
1. user opens scanner;
2. user selects/pastes sanitized blueprint;
3. scan happens locally;
4. user sees severity summary and evidence;
5. optional CTA explains the paid Data Integrity Audit.

Hosting preference:
- zero-cost static hosting where terms permit;
- no owner-funded infrastructure.

## Stage 2 — paid automated delivery

Flow:
1. self-service checkout;
2. post-purchase structured intake;
3. local/client-side preprocessing or explicit customer upload with clear consent;
4. automated static scan;
5. deterministic report generation;
6. bounded async review only for the pilot tier;
7. report delivery;
8. one re-scan link/window where included;
9. payment-provider reconciliation updates the financial ledger.

Never mark revenue as verified from an order form alone.

## Payment-provider gate

Current service-compatible candidates:
1. Stripe Payment Links;
2. Payhip;
3. Ko-fi;
4. Gumroad.

Lemon Squeezy is excluded for the current service pilot because its published prohibited-products policy excludes services. It may only be reconsidered for a compliant software/digital-product form.

Paul is required only when activation requires identity, business, bank/payout, tax, legal or contractual attestations.

## Support autonomy

Default support should be:
- structured FAQ;
- clear accepted-input rules;
- deterministic error messages;
- bounded asynchronous support;
- no production credential handling.

Repeated support questions become product rules/docs rather than permanent manual work.

## Measurement

Track separately:
- visits/source;
- scanner starts;
- completed scans;
- qualified audit intents;
- checkout starts;
- payment-provider-verified gross revenue;
- refunds;
- business-generated cash;
- reinvestment;
- expenses;
- net revenue;
- net operating result.

Do not use vanity activity counts as a substitute for paid validation.
