# Stripe Package Catalog — Prepared, Not Live

Updated: 2026-09-25

All amounts are one-time EUR prices.

## Focused Risk Check — EUR79
- Product: `prod_VKJwMo2dyS9z3U`
- Price: `price_1UJfIULEUPyOUtb0PVbLXkFt`
- Product active: false
- Price active: false
- Package metadata: `pcflows_package=focused_risk_check`
- Public payment link: not created

## Data Integrity Audit — EUR149
- Product: `prod_VKCxp4ILQhcurg`
- Price: `price_1UJYXlLEUPyOUtb0yovnfhH0`
- Existing Payment Link: `plink_1UJYXyLEUPyOUtb0elSom4yX`
- Payment Link active: false
- Package metadata now includes: `pcflows_package=data_integrity_audit`
- Existing legacy Northstar metadata retained for traceability.

## Portfolio / Release QA — EUR399
- Product: `prod_VKJwhiSWNCURAO`
- Price: `price_1UJfIWLEUPyOUtb0EfhLDC8P`
- Product active: false
- Price active: false
- Package metadata: `pcflows_package=portfolio_release_qa`
- Public payment link: not created

## Launch rule

Do not activate products/prices/payment links or expose checkout URLs until:
- official Belgian enterprise number is verified;
- VAT regime is resolved;
- public legal business identity is updated;
- package-specific checkout fields/metadata have been verified;
- safe end-to-end test is performed and excluded from revenue.

The exact package ID must match `order_contract.py` before fulfillment.
