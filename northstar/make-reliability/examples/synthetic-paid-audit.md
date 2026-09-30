# Northstar Make Data Integrity Audit

Scenario: **Synthetic order intake**

## Executive summary

Static preflight found **0 critical, 2 high, 5 medium and 1 low** findings.

Business goal: Accept each order exactly once and record the same final state in the CRM, downstream API and order ledger.

Critical side effects: Update customer/order state; POST order to downstream API; Append order to ledger

Reliability lens: prevent 3, detect 2, recover 3.

## Prioritized remediation

### 1. HIGH · RECOVER · write-without-error-handler — `http:ActionSendData` id `3`

**Evidence:** Write-like module has no exported onerror route; verify failure handling and recovery behavior.

**Why it matters:** A failed external write may stop or diverge without an explicit exported recovery path.

**Recommended next step:** Define the expected behavior for transient and permanent failure: retry, quarantine, alert, compensate, or stop deliberately.

**Verification:** Inject a synthetic downstream failure and confirm the chosen recovery path is observable and bounded.

### 2. HIGH · RECOVER · write-without-error-handler — `google-sheets:addRow` id `4`

**Evidence:** Write-like module has no exported onerror route; verify failure handling and recovery behavior.

**Why it matters:** A failed external write may stop or diverge without an explicit exported recovery path.

**Recommended next step:** Define the expected behavior for transient and permanent failure: retry, quarantine, alert, compensate, or stop deliberately.

**Verification:** Inject a synthetic downstream failure and confirm the chosen recovery path is observable and bounded.

### 3. MEDIUM · PREVENT · concurrency-review

**Evidence:** Scenario allows overlapping runs and contains write-like modules. Verify concurrent executions cannot race or duplicate writes.

**Why it matters:** Overlapping executions can race when they update the same logical record or depend on event order.

**Recommended next step:** Identify the natural business key and decide whether per-key serialization, sequential processing, optimistic checks, or idempotent writes are required.

**Verification:** Submit two safe synthetic events for the same business key concurrently and verify the final state is deterministic.

### 4. MEDIUM · PREVENT · http-write-idempotency-review — `http:ActionSendData` id `3`

**Evidence:** HTTP POST can mutate external state; verify duplicate protection/idempotency before retries.

**Why it matters:** POST/PUT/PATCH/DELETE requests can change remote state and may be unsafe to repeat without endpoint-specific duplicate protection.

**Recommended next step:** Document the endpoint's idempotency semantics and add a stable business key or idempotency mechanism before enabling retries.

**Verification:** Repeat a synthetic request with the same business key and verify the remote system does not create an unintended duplicate.

### 5. MEDIUM · PREVENT · retrying-write-idempotency-review — `crm:updateContact` id `2`

**Evidence:** Write-like module has an automatic retry handler. Verify a retry cannot duplicate or repeat an external side effect.

**Why it matters:** Automatic retry can repeat an external side effect if the first attempt actually committed before the failure became visible.

**Recommended next step:** Add an idempotency key, upsert/deduplication guard, or pre-write existence check appropriate to the destination semantics.

**Verification:** Replay the same synthetic business event twice and confirm only the intended final state/side effect exists.

### 6. MEDIUM · RECOVER · incomplete-executions-disabled-review

**Evidence:** Exported scenario has dlq=false. Verify that disabling stored incomplete executions is intentional for a workflow with external writes.

**Why it matters:** External writes exist while stored incomplete-execution recovery is exported as disabled, reducing one recovery path after failures.

**Recommended next step:** Confirm the recovery strategy explicitly and enable incomplete executions when appropriate for the scenario's failure model.

**Verification:** Trigger a safe synthetic failure after input acceptance and verify the work can be located and resumed/replayed according to policy.

### 7. MEDIUM · DETECT · filtered-write-silent-skip-review — `crm:updateContact` id `2`

**Evidence:** A filter gates a write-like module. Verify that a non-match cannot produce a business-level silent success.

**Why it matters:** A bundle can be filtered out before a business write, which may look like successful scenario execution while the expected side effect never occurs.

**Recommended next step:** Make the non-match path explicit: count it, log it, alert on unexpected volume, or route it to a review queue.

**Verification:** Provide a synthetic non-matching event and verify operators can distinguish an intentional skip from a missing write.

### 8. LOW · DETECT · confidential-observability-review

**Evidence:** Keep-data-confidential is enabled. Verify external observability exists because Make execution logs retain less payload detail.

**Why it matters:** Confidential execution settings reduce payload visibility in platform logs, which can make incident diagnosis harder.

**Recommended next step:** Keep confidentiality if required, but define privacy-safe correlation IDs, counters and failure metadata outside sensitive payloads.

**Verification:** Run a synthetic failure and confirm an operator can identify the affected business event without exposing sensitive content.

## Verification checklist

- Use only sanitized/synthetic test events.
- Exercise each affected write path at least once.
- Replay duplicate business events where duplicate protection matters.
- Exercise transient and permanent downstream failures separately.
- Confirm skips, retries and recovery events are observable without exposing sensitive payloads.
- Re-export and re-run the static scan after remediation.

## Scope and limitations

This report is deterministic static analysis of a sanitized blueprint plus optional non-sensitive context. It does not access production systems and cannot prove runtime correctness, authorization, third-party availability, business semantics, or the absence of defects.
