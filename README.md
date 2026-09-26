# n8n Workflow Reliability Audit

[![Public tests](https://github.com/Paullz94/n8n-workflow-reliability-audit/actions/workflows/test.yml/badge.svg)](https://github.com/Paullz94/n8n-workflow-reliability-audit/actions/workflows/test.yml)

A deterministic, dependency-free toolkit for reviewing exported n8n workflow JSON without credentials or production access.

## Free browser quick scan

The repository now includes a zero-backend browser scanner in [index.html](index.html). When GitHub Pages is enabled for this repository, the intended public URL is:

**https://paullz94.github.io/n8n-workflow-reliability-audit/**

The browser scanner parses a selected JSON export locally in the browser. It does not intentionally upload the workflow file. It is a lightweight heuristic lead-in, not production certification.

## What the full analyzer checks

It currently checks structure/reachability, duplicate names, active workflows without an error workflow, unauthenticated webhooks, HTTP timeouts/retries, powerful nodes, possible hard-coded secrets, and a heuristic absence of duplicate prevention before side effects.

The included unsafe order-intake fixture produces 1 critical, 4 high, 3 medium, and 1 low finding. Its hardened counterpart produces no static findings. Other fixtures demonstrate scheduled-sync recovery risks, invalid duplicate node names, and a credential-free runtime smoke path.

Runtime verification uses n8n 2.40.6: the hardened, unsafe-order, scheduled-sync, and smoke exports import successfully; the deliberately ambiguous duplicate-name fixture is rejected by n8n with the same issue the static audit reports. The smoke workflow also executes locally and must return `{"status":"ok"}`.

## Run

```powershell
python audit.py examples/unsafe_order_intake.json `
  --output examples/unsafe_order_intake.audit.md `
  --json-output examples/unsafe_order_intake.audit.json
```

## Boundary

Static review is not production certification. It cannot verify instance settings, real credential scopes, remote APIs, business rules, or runtime side effects. A production review additionally requires synthetic execution tests, credential-scope confirmation, recovery verification, and independent acceptance evidence.

Do not provide plaintext secrets or real personal data. When the scanner finds a credential-like literal, the report includes only its parameter path and the words `value redacted`.

## Test

From this directory:

```powershell
python -m unittest discover -s tests -v
```

The project intentionally uses only the Python standard library.

The same tests run on every public push and pull request using a standard GitHub-hosted Linux runner. The workflow has read-only repository permissions, a five-minute timeout, no cache/artifact storage, and pinned official action revisions.

## PCFlows service

The analyzer is the public proof artifact behind a fixed-scope B2B reliability service.

- **n8n Reliability Audit — EUR 249:** one sanitized workflow export up to 30 nodes, prioritized findings, manual review, synthetic verification plan, and one re-scan after remediation.
- **n8n Reliability Retrofit — EUR 890:** one accepted reliability risk, bounded remediation, synthetic before/after evidence, rollback notes, handoff, and one revision.

See [SERVICE.md](SERVICE.md), [BUSINESS_ENGINE.md](BUSINESS_ENGINE.md), [SALES_PLAYBOOK.md](SALES_PLAYBOOK.md), and [LAUNCH_GATE.md](LAUNCH_GATE.md) for scope, boundaries, operating rules, acquisition, qualification, and the owner-only pre-launch gate.

Stripe checkout is technically staged behind a fail-closed launch switch. The owner has confirmed the Belgian registration/social-insurance/tax prerequisites are in order; checkout remains hidden until seller-config.js contains the explicitly supplied public seller identity and checkoutEnabled is set to true.

To ask whether an existing workflow fits, [open an audit-request issue](../../issues/new?template=workflow-audit-request.yml) or email **pcmotionstudios@gmail.com**. Share metadata only—never credentials, customer data, private workflow exports, or confidential logs in a public issue.\n\nPaid orders use [intake.html](intake.html) and the deterministic [package_audit.py](package_audit.py) delivery-pack generator. See [FULFILLMENT_RUNBOOK.md](FULFILLMENT_RUNBOOK.md) for the payment-to-delivery flow.
\n\n## Final launch handoff\n\nThe remaining owner input is intentionally isolated in [SELLER_IDENTITY_HANDOFF.md](SELLER_IDENTITY_HANDOFF.md). Public seller data is never inferred from connected accounts.\n