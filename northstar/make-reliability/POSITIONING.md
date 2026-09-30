# Positioning — Make Reliability & Data Integrity

Updated: 2026-09-25

## Category decision

Northstar will **not** compete as a generic Make.com blueprint linter.

Recent market research found low-cost static linters that already inspect exported Make blueprints for broad correctness, cost, security and basic error-handling rules. That makes a generic "24 checks" product easy to commoditize.

Northstar instead focuses on the narrower, higher-consequence question:

> **Can this scenario fail, retry, race, silently skip work, or recover in a way that creates bad business data?**

## Free vs paid boundary

### Free: Privacy-first Reliability Preflight

Purpose:
- qualify inbound users;
- prove technical credibility;
- collect aggregate rule-hit counts only if a future user explicitly opts in;
- give useful value without requiring credentials or production access.

Characteristics:
- local/offline scan of a sanitized Make blueprint;
- no Make API token required;
- deterministic static checks;
- no claim that runtime correctness is proven;
- no upload required for the core scanner.

### Paid: Data Integrity Audit

Primary value:
- interpret reliability findings in business-impact order;
- map retries/concurrency/error routes to duplicate-write, overwrite, lost-update and silent-success risks;
- produce a remediation sequence;
- accept redacted/synthetic fixtures only;
- re-scan once after remediation in the initial pilot.

The paid layer must become increasingly automated. Human review is permitted only during the time-bounded willingness-to-pay pilot.

## Differentiators

1. **Privacy by default**
   - Base scan runs locally.
   - No production credentials.
   - No third-party account connection required.

2. **Data-integrity focus**
   - Duplicate side effects.
   - Retry/idempotency risk.
   - Concurrent write races.
   - Silent skips caused by filters/routes.
   - Incomplete-execution and recovery configuration.
   - Logging/observability trade-offs.

3. **Evidence, not generic advice**
   - Every finding names the rule, severity, module/path when available, and why it matters.
   - Recommendations remain scoped to what static evidence supports.

4. **Recovery-oriented output**
   - Findings are grouped into prevent / detect / recover.
   - Paid reports prioritize the safest remediation order.

5. **No false assurance**
   - Static scanning cannot validate credentials, third-party uptime, live data, business semantics or runtime behavior.
   - Reports state these limitations explicitly.

## Competitive response gate

Do not race competitors on number of rules or lowest unit price.

Continue if at least one of the following is validated:
- buyers pay for data-integrity/reliability interpretation rather than raw lint findings;
- privacy/local scanning materially improves conversion;
- remediation ordering and re-scan are valued;
- a repeatable self-service workflow can deliver the majority of value without Paul.

Pivot if qualified buyers consistently treat the product as interchangeable with low-cost generic linters and reject the differentiated outcome.
