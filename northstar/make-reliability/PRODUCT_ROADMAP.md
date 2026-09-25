# PCFlows Product Roadmap — Evidence Before Expansion

Updated: 2026-09-25

This roadmap is deliberately gated by real customer evidence. It is not a promise to build every layer.

## Stage 0 — current / ready for launch after registration

### Free Reliability Preflight
Input:
- sanitized Make.com blueprint.

Output:
- deterministic findings;
- severity + module/path evidence;
- downloadable JSON/Markdown.

Key differentiation:
- local core scan;
- Make-specific reliability semantics;
- no generic health score;
- no production credentials.

### EUR 149 Data Integrity Audit
Input:
- sanitized blueprint;
- allowlisted non-sensitive business context.

Output:
- prioritized prevent/detect/recover report;
- verification checklist;
- one re-scan;
- optional AI-assisted interpretation from a privacy-bounded packet only.

Success gate:
- real provider-verified external payments;
- delivery remains bounded;
- support burden stays low.

## Stage 1 — only after static-audit WTP is proven

### Sanitized Runtime Evidence Review

Why:
Competing Make reliability tools demonstrate that runtime/log comparison can expose problems a static blueprint cannot see.

Potential input:
- sanitized blueprint;
- one known-good execution sample;
- one failed or suspicious execution sample.

Potential checks:
- module-by-module output shape changes;
- count/volume anomalies;
- changed null/empty fields;
- status-code vs business-result mismatch;
- fallback/handler paths actually taken;
- runtime evidence that confirms or weakens static findings.

Important:
- do not ask for production credentials;
- do not create an always-on monitoring backend yet;
- prefer local or explicitly customer-supplied sanitized evidence.

Build gate:
At least 3 paid audits independently expose the same class of high-value question that cannot be answered statically.

## Stage 2 — only after repeated paid demand

### Portfolio / agency review

Potential buyer:
- automation freelancers;
- Make agencies;
- small operations teams with multiple scenarios.

Potential value:
- consistent portfolio report;
- recurring finding taxonomy;
- before/after remediation comparison;
- client-facing export.

Build gate:
Real customers request more than one scenario and are willing to pay for repeatable portfolio analysis.

## Stage 3 — only if recurring monitoring is demanded

### Reliability Watch / anomaly monitoring

Potential value:
- detect unusual successful runs;
- record-count swings;
- operation/credit spikes;
- recurring silent-skip patterns;
- regression alerts.

Why this is late:
- needs live data/API integration;
- creates ongoing support/privacy/infrastructure obligations;
- risks turning PCFlows into an operator-heavy SaaS before WTP is proven.

Build gate:
Business-generated revenue funds the infrastructure and at least several customers explicitly request ongoing monitoring.

## Explicit non-goals for the pilot

Do not build yet:
- broad Make scenario builder;
- generic AI automation consultant;
- n8n/Zapier parity;
- production credential vault;
- live incident response;
- generic chatbot;
- expensive model/API dependency;
- full observability platform.

Northstar optimizes for a narrow product that can reach EUR 1,000 verified gross revenue before widening scope.
