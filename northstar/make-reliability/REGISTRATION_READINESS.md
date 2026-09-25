# Registration-to-Paid-Launch Readiness

Updated: 2026-09-25

This checklist exists to prevent the live Stripe checkout from reopening before the Belgian registration, VAT and e-commerce disclosure gates are actually complete.

## Current state

- Planned activity start: 2026-10-01.
- Xerius self-employed affiliation: approved.
- Enterprise number: pending.
- Stripe live Payment Link: intentionally inactive.
- Public site: free scanner / no-payment interest only.

## When the enterprise number arrives

Verify against the official Xerius/KBO confirmation:
- legal operator / natural person registration;
- trade name PCFlows;
- enterprise number;
- official start date;
- registered activity codes;
- establishment address.

Do not infer any of these from the application draft if the official confirmation differs.

## VAT decision gate

Do **not** assume the Belgian small-enterprise VAT exemption will be available from 2026-10-01.

FOD Financiën currently states that, for an existing choice to apply the Belgian small-enterprise exemption from 1 October 2026, the e604 choice deadline is 15 September 2026. Because the registration application was submitted after that date, verify the exact treatment through Xerius/e604 once the enterprise number exists.

Possible outcomes to confirm:
- normal VAT regime for Q4 2026, with a later exemption change when legally effective; or
- another start/new-registration treatment explicitly accepted by the administration.

Do not reopen paid checkout until the VAT treatment is known and pricing/invoicing are configured accordingly.

Official source:
https://financien.belgium.be/nl/ondernemingen/btw/btw-plicht/vrijstellingsregeling

## Website identification gate before online sales

FOD Economie requires business-identification information to be easily, directly and permanently accessible on business websites/social pages.

Before paid launch, add the confirmed:
- trade/business name;
- establishment address;
- at least two direct contact methods; for online services this includes email and phone;
- enterprise number;
- VAT identification/status where applicable.

Official source:
https://economie.fgov.be/nl/themas/online/elektronische-handel/verkoop-internet/bedrijfswebsite-en-accounts-op

## Consumer distance-selling gate

If PCFlows accepts consumer customers online, the checkout/service flow must handle Belgian distance-selling information obligations.

Before a consumer becomes bound, clearly disclose:
- service characteristics;
- total price including applicable taxes;
- payment/delivery arrangements;
- withdrawal/cancellation rights.

For a service that a consumer wants started during the 14-day withdrawal period, FOD Economie states that the consumer must expressly request early performance and acknowledge that the withdrawal right ends once the service has been fully performed.

Official sources:
https://economie.fgov.be/nl/themas/ondernemingen/guidance/handelspraktijken/informatieverplichting-bij-e/veelgestelde-vragen-over-de
https://economie.fgov.be/nl/themas/verkoop/vormen-van-verkoop/verkoop-internet-e-commerce

## Reopen checkout only when

- [ ] Enterprise number confirmed.
- [ ] Official economic-activity start date reached (currently planned **2026-10-01**); no paid orders before that effective date.
- [ ] VAT regime/effective date confirmed.
- [ ] Website carries required business identity/contact information.
- [ ] Consumer withdrawal/start-of-service wording is configured if B2C sales are accepted.
- [ ] Stripe price/tax/invoice behavior matches the confirmed VAT regime.
- [ ] Post-payment intake/delivery instructions are live.
- [ ] Revenue ledger reconciliation remains provider-verified.

Until then, keep validation free/no-payment.
