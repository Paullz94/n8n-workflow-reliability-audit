# Revenue Ledger Policy

Updated: 2026-09-25

The EUR 1,000 success gate is deliberately stricter than a normal order counter.

## Target-eligible revenue

A payment contributes to `verified_gross_revenue` only when all are true:
- real external customer;
- EUR-denominated during the pilot;
- payment-provider status is paid/succeeded/settled;
- provider verification has been recorded;
- not a test transaction;
- not an owner transaction;
- no successful refund exists for that payment.

**Strict refund rule:** if any completed refund exists, the entire payment is disqualified from the EUR 1,000 target. This is intentionally conservative.

## Separate metrics

- `provider_collected_external_gross`: verified external collections before successful refunds.
- `verified_gross_revenue`: strict target-eligible gross as defined above.
- `refunds`: successful refund amounts.
- `net_revenue`: verified external collections less completed refund amounts.
- `revenue_reinvested`: expenses explicitly funded by business revenue.
- `expenses`: all confirmed business expenses regardless of funding source.
- `business_generated_cash`: net revenue less revenue-funded reinvestment.
- `net_operating_result`: net revenue less all expenses.
- `owner_capital_injected`: only confirmed injections with explicit Paul approval.
- `owner_reserve_uninjected`: EUR 500 less confirmed owner-capital injections.

## Owner-capital gate

The engine rejects a confirmed owner-capital event unless `approved_by_paul=true`.
It also rejects owner injections above the EUR 500 reserve ceiling.

This flag is accounting evidence only; Paul still must actually give explicit approval before any such event is created.

## Journal model

The journal is append-only and uses stable event IDs. Duplicate IDs are rejected.

Payment-provider exports/webhooks must eventually be normalized into the journal. A manual order form, invoice, promise to pay, screenshot, pending authorization, or self-reported sale is insufficient provider verification.
