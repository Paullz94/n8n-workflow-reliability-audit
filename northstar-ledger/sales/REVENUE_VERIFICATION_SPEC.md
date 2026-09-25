# Revenue Verification Spec

## Goal metric

Northstar succeeds only when qualifying gross revenue reaches at least EUR 1,000.

A transaction qualifies only when all conditions are true:

1. Customer is an unrelated external buyer.
2. Payment is live, not test mode.
3. Payment provider reports the charge as successfully paid/captured/settled, not merely initiated or pending.
4. The transaction is not an owner/self purchase.
5. The transaction is not fictitious, promotional-only, or zero-value.
6. The payment has not been refunded.

If a previously qualifying transaction is later refunded, its qualifying gross revenue is reversed for goal tracking and the refund is recorded separately.

## Sources of truth

Phase 1:
- Stripe transaction/payment record for payment state and amount.
- Payhip order record for purchased product, delivery, and marketplace eligibility.
- Payhip refunded webhook/order state when applicable.

Do not infer revenue from email receipts, page views, checkout starts, GitHub stars, downloads, comments, or screenshots alone.

## Ledger mapping

- gross_revenue_eur: currently qualifying live external revenue.
- owner_reserve_eur: owner's uninjected reserve; never business cash.
- owner_capital_injected_eur: only money explicitly transferred/paid by owner into business operations.
- business_generated_cash_eur: customer-derived cash after recorded outflows/refunds as applicable.
- revenue_reinvested_eur: business-generated cash deliberately spent on growth/operations.
- expenses_eur: platform/processor and other business expenses.
- refunds_eur: refunded customer payments.
- net_revenue_eur: qualifying revenue less refunds and directly attributable sales deductions as tracked.
- net_operating_result_eur: net revenue less operating expenses.

## Currency

Target is EUR. For non-EUR customer transactions, store the provider-reported original amount and use a documented provider/bank EUR conversion amount when it becomes available; do not fabricate an exchange rate in the ledger.
