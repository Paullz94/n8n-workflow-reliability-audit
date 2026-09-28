# Seller identity handoff template

The owner has now supplied the Belgian enterprise/KBO number. The remaining public seller identity can be completed later using this template.

- Legal name:
- Trade name: PCFlows
- Registered business address:
- Enterprise/KBO number: 1043.055.054 — supplied by owner
- VAT status:
- VAT number (if applicable):
- Professional email:
- Professional phone:

Do not infer or publish the remaining values from Stripe, Gmail, account profiles, prior chats, or hidden personal data. Enterprise number 1043.055.054 was explicitly supplied by the owner. VAT status/number must still be confirmed separately.

After receipt:
1. fill seller-config.js;
2. set complete=true only when every required public field is present;
3. update any corresponding Stripe account/tax fields where permitted;
4. activate both staged Payment Links;
5. set checkoutEnabled=true in launch-config.js;
6. run CI;
7. merge;
8. verify the public legal page and checkout-to-intake path;
9. begin compliant B2B acquisition.
