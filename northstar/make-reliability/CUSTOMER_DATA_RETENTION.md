# PCFlows Customer Data Retention & Isolation Policy — Internal

Updated: 2026-09-25

## Design goal

PCFlows should remain useful even if it grows to many customers without creating a shared pool of customer content that an AI can accidentally cross-reference.

## Data classes

### A. Raw/sanitized customer technical artifacts
Examples:
- sanitized Make blueprint;
- sanitized execution evidence;
- revised blueprint submitted for re-scan.

Default design:
- case-scoped only;
- never public;
- never committed to GitHub;
- never placed in a shared cross-customer vector store;
- never used as a reusable example for another customer;
- excluded from AI-review packets unless reduced to deterministic allowlisted evidence;
- retain only for the active service/re-scan window where operationally necessary;
- target deletion after the bounded service window ends, unless a legal/security hold requires otherwise.

### B. Derived technical evidence
Examples:
- deterministic findings;
- hashes;
- rule IDs;
- verification statuses;
- non-sensitive aggregate counts.

May be retained longer when useful for:
- audit trail;
- dispute handling;
- product-quality metrics.

Do not retain customer payload values inside derived evidence.

### C. Billing/business records
Examples:
- Stripe transaction IDs;
- invoices;
- customer billing identity where legally required.

Keep separately from technical workflow artifacts and retain according to applicable legal/accounting obligations.

### D. Support communications
Keep only as long as needed for support, dispute handling, and applicable legal/business obligations. Avoid copying customer technical payloads into email bodies.

## Default 30-day technical window

The current paid audit includes a re-scan expected within 30 days.

A future persistent storage implementation should therefore use a default technical-artifact expiry aligned to that service window:
- active case: available only inside that case namespace;
- after re-scan or service-window expiry: queue raw technical artifacts for deletion;
- keep only non-sensitive hashes/findings/financial records as justified.

This 30-day technical-artifact target is an operational privacy default, not a statement about statutory accounting retention.

## Cross-customer isolation

Every paid order receives a pseudonymous `case_scope_id`.

Any persistent storage layer must make `case_scope_id` a mandatory partition key.

A query without a current case scope must not be able to retrieve customer technical artifacts.

No retrieval-augmented AI prompt should search across customer cases.

## AI memory rule

Do not intentionally feed one customer's technical details into another customer's conversation, prompt, report, or repair plan.

Product learning should use:
- rule-frequency counts;
- anonymized aggregate outcomes;
- synthetic fixtures.

Not:
- copied customer blueprints;
- customer prompts;
- customer CRM exports;
- live payload examples.

## Incident response

If PCFlows ever detects a possible cross-case data mix-up:
1. stop automated delivery for the affected case;
2. freeze the involved technical artifacts from further AI processing;
3. identify which case scopes were involved;
4. do not silently overwrite or hide evidence;
5. follow applicable incident/breach obligations;
6. only resume automation after the containment root cause is fixed and tested.
