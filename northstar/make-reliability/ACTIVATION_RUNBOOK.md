# PCFlows Activation Runbook — After Enterprise Number

Prepared: 2026-09-25

Use this only after Xerius issues the official Belgian enterprise number. Re-check current official guidance at execution time.

## Phase 1 — verify official registration

1. Record the enterprise number privately.
2. Verify the KBO public record:
   - legal/natural-person enterprise identity;
   - PCFlows trade name if published;
   - establishment unit;
   - registered activities;
   - official start date.
3. If the KBO record is materially wrong, resolve it with Xerius before paid launch.

Official KBO public search:
https://kbopub.economie.fgov.be/

## Phase 2 — VAT identification

FPS Finance sequence:
- enterprise number first;
- then VAT identification through e604 / form 604A;
- before the economic activity begins;
- FPS Finance advises allowing KBO data to propagate before filing.

Target for the pilot, if accepted based on the actual e604A situation:
- VAT identification;
- small-enterprise exemption regime;
- no ordinary VAT charged under that regime;
- official VAT/enterprise number retained on required business records.

Do not guess if the portal options differ from the prepared research. Capture the actual screen and resolve ambiguity before launch.

Official source:
https://financien.belgium.be/nl/ondernemingen/btw/aangifte/aanvang-wijziging-einde-activiteit

## Phase 3 — public business identity

After official details are verified:
- add required enterprise/VAT identity information to the PCFlows site;
- add or update required business contact details;
- reconcile Stripe account/business profile with the official registration;
- keep support email: PCMotionstudios@gmail.com;
- keep statement descriptor PCFLOWS if accepted by Stripe.

Do not publish unnecessary personal information beyond legal requirements.

## Phase 4 — invoicing

Before an in-scope Belgian B2B invoice:
1. re-check the current official Belgian Peppol software list;
2. choose one smallest adequate free/low-cost provider;
3. register the enterprise on Peppol through that provider;
4. confirm send/receive capability;
5. keep invoice and delivery evidence privately.

Current shortlist is in PEPPOL_SHORTLIST.md.

Do not buy Dexxter or another subscription solely because it is convenient unless the zero/low-cost route proves inadequate.

## Phase 5 — safe checkout test

Before reactivating public checkout:
- verify Stripe charges/payouts remain enabled;
- verify the EUR 149 product/price;
- verify billing address collection;
- verify Scenario name field;
- verify Buying as classification;
- verify tax-ID collection behavior;
- verify post-payment redirect contains Checkout Session ID;
- verify the thank-you page/email handoff;
- verify the test is clearly owner/test and cannot enter verified gross revenue.

Do not count the checkout test toward Northstar revenue.

## Phase 6 — launch

Only after the above:
- reactivate the Stripe Payment Link;
- replace the disabled website CTA with the real checkout button;
- verify the live page once;
- launch one acquisition surface at a time;
- keep Make Community autonomous activity research-only under its current rules;
- do not mass-post or bulk-DM.

## Phase 7 — first real order

For every first-pilot order:
1. verify Stripe payment is genuine/external/live;
2. collect sanitized blueprint + local intake JSON;
3. run qualification gate;
4. hard-stop on secret-like input;
5. run deterministic audit;
6. create AI-review packet for bounded interpretation;
7. QA against deterministic evidence;
8. generate delivery ZIP;
9. deliver;
10. reconcile provider payment into the strict Northstar ledger;
11. record support/delivery time privately;
12. later perform one included before/after re-scan if requested.

## First-customer measurement

For each order track privately:
- acquisition source;
- date;
- checkout started/completed;
- qualification route;
- time spent on manual QA;
- support messages required;
- refund/chargeback status;
- whether re-scan is used;
- customer objection/questions.

These observations determine whether PCFlows should automate further, change price, or pivot.
