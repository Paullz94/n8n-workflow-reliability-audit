# n8n Workflow Reliability Audit

A deterministic, dependency-free portfolio artifact for reviewing exported n8n workflow JSON without credentials or production access. It produces redacted Markdown and JSON findings.

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

## Fixed-scope audit service

The analyzer is also the proof artifact for a small, manual reliability-audit pilot. See [SERVICE.md](SERVICE.md) for scope, boundaries, pricing hypotheses, and delivery process.

To ask whether an existing workflow fits, [open an audit-request issue](../../issues/new?template=workflow-audit-request.yml). Share metadata only—never credentials, customer data, private workflow exports, or confidential logs in a public issue.
