# Belgian Launch Compliance Notes — PCFlows

Research date: 2026-09-25  
Purpose: operational checklist, not individualized tax/legal advice.

## Current registration state

- planned sole-proprietor start date: 2026-10-01;
- Xerius self-employed affiliation: approved;
- enterprise number: pending;
- no paid launch until the enterprise-number/VAT identification gate is complete.

## VAT identification sequence

Official FPS Finance guidance states that a new Belgian VAT activity requires:
1. an enterprise number in the Crossroads Bank for Enterprises (KBO);
2. a VAT identification request (e604A).

The e604A should be filed after the KBO registration and before the economic activity starts. FPS Finance advises filing the VAT-identification request at least two days after KBO registration.

Source:
https://financien.belgium.be/nl/ondernemingen/btw/aangifte/aanvang-wijziging-einde-activiteit

## Small-enterprise VAT exemption

PCFlows' activity is not obviously in one of the sectors excluded from the small-enterprise exemption.

For a **new enterprise**, the official 2026 brochure explains that the estimated turnover is supplied in the initial 604A and compared with the EUR 25,000 threshold, pro-rated for the remaining operating period.

For a 2026-10-01 start, 92 calendar days remain through 2026-12-31. The indicative pro-rata threshold is approximately EUR 6,301.37. The initial PCFlows EUR 1,000 gross-revenue validation target is well below that amount.

Primary sources:
- https://financien.belgium.be/nl/ondernemingen/btw/btw-plicht/vrijstellingsregeling
- https://financien.belgium.be/sites/default/files/downloads/123-brochure-vrijstellingsregeling-belasting.pdf

Important distinction:
- FPS Finance publishes quarterly change deadlines (15 March / June / September / December) for choosing the regime at quarter boundaries.
- The 2026 official brochure separately describes **new enterprises** choosing the regime through their initial 604A based on estimated turnover.
- Do not assume an existing-enterprise switch deadline automatically blocks a genuinely new-enterprise 604A. Follow the actual e604A options shown after the enterprise number is issued; if ambiguous, obtain written clarification from FPS Finance/Xerius before charging customers.

## E-invoicing / Peppol

Since 2026, Belgian VAT-identified businesses generally need structured electronic invoices for in-scope Belgian B2B transactions. The obligation also applies when the supplier uses the small-enterprise VAT exemption.

A PDF alone is not the legally required structured invoice for in-scope Belgian B2B sales.

PCFlows therefore needs a Peppol-capable solution before the first in-scope Belgian B2B invoice.

Official sources:
- https://efactuur.belgium.be/nl/article/gestructureerde-elektronische-facturen-tussen-ondernemingen-verplicht-sinds-2026
- https://efactuur.belgium.be/nl/FAQ/algemene-vragen-b2b
- https://efactuur.belgium.be/nl/article/softwareoplossingen-voor-het-verzenden-ontvangen-en-verwerken-van-elektronische-facturen

The Belgian government does not provide one central free invoicing application; it publishes a market list that includes some free/low-cost options.

Do not buy a bookkeeping/e-invoicing subscription before:
1. the enterprise/VAT number exists;
2. actual customer type is known;
3. a zero/low-cost compliant option has been checked.

## Launch gate

Before re-enabling Stripe:
- [ ] enterprise number received;
- [ ] KBO record verified;
- [ ] e604A VAT identification submitted/accepted;
- [ ] VAT regime confirmed;
- [ ] enterprise/VAT information added to site/records as required;
- [ ] Peppol-capable invoicing route selected before an in-scope Belgian B2B invoice;
- [ ] Stripe account business information reconciled with the official registration;
- [ ] checkout test completed without counting it as revenue.

## International customers

International B2B/B2C VAT and invoicing treatment can differ from domestic Belgian transactions. Do not infer the tax treatment from the customer's Stripe payment alone. Preserve billing country/tax-ID evidence where needed and obtain specific guidance for cases outside the simple Belgian pilot path.
