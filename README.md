# n8n Workflow Reliability Audit

A deterministic, dependency-free portfolio artifact for reviewing exported n8n workflow JSON without credentials or production access. It produces redacted Markdown and JSON findings.

It currently checks structure/reachability, duplicate names, active workflows without an error workflow, unauthenticated webhooks, HTTP timeouts/retries, powerful nodes, possible hard-coded secrets, and a heuristic absence of duplicate prevention before side effects.

The included unsafe order-intake fixture produces 1 critical, 4 high, 3 medium, and 1 low finding. Its hardened counterpart produces no static findings. Other fixtures demonstrate scheduled-sync recovery risks and ambiguous duplicate node names.

## Run

```powershell
python -m app.workflow_audit.audit app/workflow_audit/examples/unsafe_order_intake.json `
  --output app/workflow_audit/examples/unsafe_order_intake.audit.md `
  --json-output app/workflow_audit/examples/unsafe_order_intake.audit.json
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

