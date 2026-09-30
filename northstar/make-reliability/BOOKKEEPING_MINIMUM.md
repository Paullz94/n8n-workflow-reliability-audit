# PCFlows Minimal Bookkeeping Plan

Updated: 2026-09-25

Goal: keep the pilot administratively simple without paying for a full bookkeeping subscription before it is justified.

This does not replace statutory accounting/tax obligations.

## Separate evidence sets

Keep these separate:

### 1. Sales / income
For each real customer order retain:
- invoice / structured e-invoice reference where required;
- date;
- customer classification (B2C / Belgian B2B / foreign B2B);
- customer country;
- gross amount;
- VAT regime/treatment;
- Stripe PaymentIntent/Checkout Session reference;
- Stripe fee;
- refund/chargeback status;
- net payout.

### 2. Expenses
Retain:
- supplier document;
- date;
- supplier;
- description/business purpose;
- gross amount;
- VAT amount if present;
- payment evidence;
- funding source: owner capital or business-generated cash.

Do not infer an expense merely because a price was quoted. Record it when there is actual evidence of the expense.

### 3. Bank / Stripe reconciliation
At least monthly, reconcile:
- Stripe successful payments;
- Stripe fees;
- Stripe refunds/disputes;
- Stripe payouts;
- business bank transactions.

The Northstar revenue ledger is intentionally stricter than accounting revenue and exists only for the EUR 1,000 validation gate. It does **not** replace bookkeeping.

## Internal CSV format

A simple private local CSV can use:

```
date,type,document_ref,counterparty,country,customer_type,description,gross_eur,vat_eur,stripe_fee_eur,refund_eur,net_cash_eur,funded_by,provider_ref,notes
```

Never commit the populated bookkeeping file to the public GitHub repository.

## Invoicing

- B2C: structured Belgian B2B e-invoicing rules do not generally require an outgoing Peppol invoice merely because the seller has a VAT number, but ordinary invoice/consumer rules still apply.
- Belgian in-scope B2B: use a Peppol-capable structured e-invoicing solution.
- Foreign customers: determine VAT/invoicing treatment based on the actual customer and location; do not guess.

## Cost policy

Before purchasing bookkeeping software:
1. use the smallest compliant workflow;
2. check government-listed Peppol solutions for free/low-cost options;
3. measure actual monthly invoice volume;
4. only request owner-capital spend if the free/cheaper route is inadequate and the exact cost is justified.
