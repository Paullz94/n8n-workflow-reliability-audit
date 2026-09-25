# Package Consistency Guard

Updated: 2026-09-25

`package_consistency.py` prevents pricing/scope drift between:
- `package_catalog.json`;
- the strict paid `order_contract.py`.

The guard fails if:
- a paid package exists in one but not the other;
- EUR display price and Stripe cents contract disagree;
- the free preflight is missing or no longer EUR0.

Current contract:
- Focused Risk Check: EUR79
- Data Integrity Audit: EUR149
- Portfolio / Release QA: EUR399
- Reliability Preflight: EUR0

The website remains a presentation layer. Before checkout activation, its visible prices must also be manually/source-QA checked against this contract.
