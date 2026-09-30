# Stripe Checkout Package Adapter

Updated: 2026-09-25

Stripe package metadata may be present on different trusted objects depending on the checkout path.

`stripe_checkout_adapter.py` normalizes authenticated Stripe data before it reaches `order_contract.py`.

Supported package metadata sources:
- Checkout Session metadata;
- expanded PaymentIntent metadata;
- line-item Price metadata;
- expanded Product metadata under the Price.

Rules:
- provider data must come from authenticated Stripe access;
- conflicting package IDs hard-stop;
- missing package metadata hard-stops;
- owner/test flags hard-stop;
- amount/currency/payment/live checks are delegated to the strict order contract.

This lets package fulfillment remain deterministic even if the exact Stripe object carrying metadata differs between Payment Links or later Checkout implementations.
