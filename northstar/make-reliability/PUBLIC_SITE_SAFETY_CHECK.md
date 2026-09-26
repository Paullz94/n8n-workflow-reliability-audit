# Public Site Safety Check

Checked: 2026-09-25

Scope:
- docs/index.html
- docs/scanner.html
- docs/scanner-core.js
- docs/intake.html

Static checks:
- scanner page contains no fetch() call;
- scanner core contains no fetch() call;
- no XMLHttpRequest usage;
- no WebSocket usage;
- intake generator contains no fetch() call;
- no remote JavaScript dependency in the public home/scanner/intake pages;
- no live Stripe buy.stripe.com link is exposed on the public home page while registration is pending.

The live Stripe Payment Link itself is also inactive at provider level.

This check is static and does not replace browser/runtime testing.
