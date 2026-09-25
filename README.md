# n8n Workflow Reliability Audit

[![Public tests](https://github.com/Paullz94/n8n-workflow-reliability-audit/actions/workflows/test.yml/badge.svg)](https://github.com/Paullz94/n8n-workflow-reliability-audit/actions/workflows/test.yml)

A deterministic, dependency-free portfolio artifact for reviewing exported n8n workflow JSON without credentials or production access. It produces redacted Markdown and JSON findings.

The scanner focuses on reliability failure modes that can survive a happy-path demo:

- invalid or ambiguous workflow structure;
- unreachable nodes and stale connection references;
- active workflows without a workflow-level error workflow;
- unauthenticated webhooks;
- HTTP calls without explicit timeouts or node retry policy;
- failures that can be converted into apparently successful executions;
- disabled or powerful nodes that need manual review;
- possible hard-coded secrets, with values always redacted;
- side effects reachable without an explicit duplicate/replay guard;
- retry-enabled mutating HTTP calls that have no visible upstream idempotency guard.

Duplicate-prevention analysis is graph-aware: a deduplication-looking node on an unrelated branch, or after the side effect, does not hide an unguarded path. Read-only HTTP methods such as GET/HEAD/OPTIONS are not treated as side effects.

The included unsafe order-intake fixture produces 1 critical, 4 high, 3 medium, and 1 low finding. Its hardened counterpart produces no critical or high findings. Other fixtures demonstrate scheduled-sync recovery risks, invalid duplicate node names, and a credential-free runtime smoke path.

Runtime verification uses n8n 2.40.6: the hardened, unsafe-order, scheduled-sync, and smoke exports import successfully; the deliberately ambiguous duplicate-name fixture is rejected by n8n with the same issue the static audit reports. The smoke workflow also executes locally and must return `{"status":"ok"}`.

## Run

```powershell
python audit.py examples/unsafe_order_intake.json `
  --output examples/unsafe_order_intake.audit.md `
  --json-output examples/unsafe_order_intake.audit.json
```

## CI / automation gate

The CLI can return a non-zero exit status when findings meet a chosen severity threshold:

```powershell
python audit.py examples/hardened_order_intake.json --fail-on high
```

`--fail-on high` fails for critical or high findings. Available thresholds are `critical`, `high`, `medium`, `low`, `info`, and `none` (default).

This makes the scanner usable as a lightweight regression gate around sanitized workflow exports without turning static analysis into a claim of production certification.

## Machine-readable output

JSON reports include:

- severity counts;
- workflow metadata;
- identified roots;
- reachable-node count;
- reachable side-effect nodes;
- side-effect nodes that have at least one trigger/root path without a visible replay/idempotency guard;
- ordered findings with evidence and recommendations.

The current report schema is version 2.

## Boundary

Static review is not production certification. It cannot verify instance settings, real credential scopes, remote APIs, business rules, or runtime side effects. A production review additionally requires synthetic execution tests, credential-scope confirmation, recovery verification, and independent acceptance evidence.

The graph-aware duplicate-prevention check is deliberately conservative and heuristic. It recognizes explicit deduplication/replay-prevention signals in the workflow graph, but it cannot prove the correctness of a business idempotency strategy.

Do not provide plaintext secrets or real personal data. When the scanner finds a credential-like literal, the report includes only its parameter path and the words `value redacted`.

## Test

From this directory:

```powershell
python -m unittest discover -s tests -v
```

The project intentionally uses only the Python standard library.

The same tests run on every public push to `main` and on pull requests using a standard GitHub-hosted Linux runner. The workflow has read-only repository permissions, a five-minute timeout, no cache/artifact storage, and pinned official action revisions.

## Fixed-scope audit service

The analyzer is also the proof artifact for a small, manual reliability-audit pilot. See [SERVICE.md](SERVICE.md) for scope, boundaries, pricing hypotheses, and delivery process.

To ask whether an existing workflow fits, [open an audit-request issue](../../issues/new?template=workflow-audit-request.yml). Share metadata only—never credentials, customer data, private workflow exports, or confidential logs in a public issue.
