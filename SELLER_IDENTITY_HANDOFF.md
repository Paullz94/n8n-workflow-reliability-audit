# Seller identity handoff template

The owner has already supplied or confirmed the Belgian registration and VAT-status facts needed for the current pre-launch state.

Confirmed:
- Trade name: PCFlows
- Enterprise/KBO number: 1043.055.054
- VAT status: in order per owner confirmation
- Numeric VAT identifier: intentionally private until an actual customer needs it
- Professional email: pcmotionstudios@gmail.com

Remaining values that require deliberate owner-approved publication:
- Legal seller name:
- Registered business address:
- Professional phone/contact number:

Do not infer or publish these remaining values from Stripe, Gmail, account profiles, prior chats or hidden personal data.

VAT must not be treated as a blocker and the numeric VAT identifier must not be auto-published.

After the remaining public seller values are supplied:
1. fill seller-config.js;
2. set complete=true only when every required public field is present;
3. on or after 2026-10-01, verify Stripe/KYC has no outstanding owner action;
4. activate the three canonical staged Payment Links;
5. set checkoutEnabled=true in launch-config.js;
6. run CI;
7. verify the public legal page and all checkout-to-intake paths.

Clearly labeled pre-launch B2B acquisition may run before the paid launch date.
