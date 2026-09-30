# Paid Order Contract

Updated: 2026-09-25

Paid fulfillment is package-specific and must be backed by provider truth.

`order_contract.py` validates a trusted Stripe Checkout Session snapshot before customer fulfillment.

Required:
- provider_verified = true;
- livemode = true;
- Stripe Checkout Session id;
- payment_status = paid;
- EUR currency;
- exact `pcflows_package` metadata;
- exact amount for that package;
- not owner/test.

Current package contract:
- focused_risk_check -> EUR 79.00
- data_integrity_audit -> EUR 149.00
- portfolio_release_qa -> EUR 399.00

Any amount/package mismatch hard-stops fulfillment.

This prevents:
- a lower-priced checkout triggering a larger scope;
- stale/wrong payment links routing to the wrong deliverable;
- owner/test transactions entering customer fulfillment;
- non-EUR or unverified payment snapshots being treated as paid orders.
