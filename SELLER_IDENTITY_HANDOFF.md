# Seller identity handoff template

When all technical validation is complete, the owner can provide the remaining public seller identity in one message using this template.

- Legal name:
- Trade name: PCFlows
- Registered business address:
- Enterprise/KBO number:
- VAT status:
- VAT number (if applicable):
- Professional email:
- Professional phone:

Do not infer or publish these values from Stripe, Gmail, account profiles, prior chats, or hidden personal data. Use only values the owner explicitly provides for publication.

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
