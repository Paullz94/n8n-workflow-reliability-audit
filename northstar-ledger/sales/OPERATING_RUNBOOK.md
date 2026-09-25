# Operating Runbook — Self-Service Validation Loop

## Customer path

1. Buyer discovers the free local scanner or educational launch-readiness content.
2. Buyer runs the free scanner locally with no account and no source upload.
3. Product page explains the deeper failure-path, payment-lifecycle, rollback, and remediation pack.
4. Buyer completes Payhip checkout.
5. Payhip automatically sends the download page/receipt link.
6. Stripe provides payment-provider evidence.
7. Revenue is added to the ledger only after the Revenue Verification Spec qualifies it.

## First-sale unlock

After the first genuine EUR 39 sale:
- confirm it remains qualifying and non-refunded;
- submit the store/product for Payhip Marketplace review because the published USD 10 sales threshold is crossed;
- do not create a self-purchase to reach or simulate the threshold.

## Support

Default support is bounded, asynchronous product support:
- broken/corrupt download;
- missing file;
- unclear pack instruction;
- reproducible scanner defect.

Out of scope:
- bespoke penetration testing;
- legal/compliance certification;
- unlimited code review;
- production incident ownership;
- continuous app operation.

A scanner defect should become a test first, then a bounded fix and versioned bundle update.

## Iteration gates

Use actual evidence in this order:
1. settled sales;
2. refunds/chargebacks;
3. checkout conversion signals where available;
4. support questions;
5. free-tool usage signals;
6. public reactions.

Do not buy ads or paid tooling before genuine willingness-to-pay evidence. Business-generated cash is the first reinvestment source.

## Owner touch requirement

Normal sales and file delivery must not require Paul. Owner involvement is reserved for regulated payment/KYC/tax/account actions, exceptional refunds/disputes requiring account authority, or explicit strategic approval for owner capital.
