# Competitive Intelligence — Make / Automation Reliability

Research date: 2026-09-25

Purpose: learn from current adjacent products and paid services without copying their wording, visual identity, proprietary logic, or unsupported claims.

## 1. ScenarioTrace

Public positioning:
- Make-specific reliability layer;
- free log comparison tool;
- deterministic checks plus AI-assisted reasoning;
- emphasizes failures that can hide behind successful/green runs;
- no sign-up / no Make API connection for the free analyzer;
- health report, monitoring and assertions are described as future directions.

Useful lesson for PCFlows:
- lead with the business consequence, not the parser;
- reliability is easier to understand as "green does not always mean correct";
- runtime/log evidence is a useful future layer that complements blueprint static analysis;
- deterministic rules should remain the source of repeatability; AI can assist interpretation rather than replace evidence.

PCFlows response:
- keep static blueprint analysis deterministic;
- do not claim runtime diagnosis from a blueprint;
- future roadmap may add an **optional sanitized execution-evidence comparison** after willingness-to-pay is proven;
- do not build monitoring/watchdog infrastructure before the pilot proves demand.

Source:
https://scenariotrace.com/

## 2. MakeIntegration Scenario Analyzer

Public positioning:
- free browser-local blueprint analyzer;
- health score and severity-organized findings;
- structural checks such as error handlers, router issues, complexity and operation estimates;
- explicitly explains static-analysis blind spots;
- no blueprint upload.

Useful lesson for PCFlows:
- browser-local scanning is no longer sufficient differentiation by itself;
- plain-language explanation and visible limitations increase trust;
- generic structural linting is commoditized;
- scoring can make a tool easy to understand, but can overstate certainty when static checks are incomplete.

PCFlows response:
- **do not compete on generic health score**;
- differentiate on data integrity / failure semantics:
  - retry/idempotency;
  - Skip/Ignore / Resume silent-success risk;
  - Commit/Rollback/autocommit recovery boundaries;
  - incomplete-execution/data-loss settings;
  - business-impact ordering and verification;
- keep severity + evidence rather than reducing the audit to one score.

Source:
https://www.makeintegration.com/blog/how-to-check-the-health-of-your-make-scenarios

## 3. Paid Upwork audit services

Observed current examples include:
- broad Make/n8n/Zapier workflow audits;
- reliability/error-handling/scalability reviews;
- AI automation architecture/reliability audits;
- deliverables such as prioritized findings, test plans, workflow/failure maps and fix roadmaps.

Observed published prices include:
- USD 99 starter reliability audit;
- USD 149 reliability audit/action-plan offer;
- USD 249/499 higher architecture tiers.

Useful lesson:
- customers already understand "workflow reliability audit" as a paid service category;
- a EUR 149 pilot is within the current visible service range, not an isolated invented price;
- paid competitors often broaden into rebuilds/architecture/consulting, which can turn into operator-heavy service work.

PCFlows response:
- keep the EUR 149 offer deliberately bounded;
- avoid "we can build anything" positioning;
- emphasize:
  - fixed scope;
  - sanitized blueprint;
  - no production access;
  - evidence-first findings;
  - remediation order;
  - verification checklist;
  - one re-scan;
- make the paid audit feel like a productized deliverable, not an open-ended freelance engagement.

Sources:
- https://www.upwork.com/services/product/development-it-make-n8n-workflow-audit-reliability-error-handling-scalability-review-2086829136032656148
- https://www.upwork.com/services/product/development-it-an-ai-automation-workflow-architecture-and-reliability-audit-2094042047722823830
- https://www.upwork.com/services/product/development-it-a-reliability-audit-and-action-plan-for-your-ai-automation-workflow-2096065594073314253

## 4. n8n audit products/templates

Observed:
- automated audit/export products around USD 100;
- security/reliability audit templates;
- recurring score/report concepts.

Useful lesson:
- audit automation itself is monetizable;
- users value exportable reports, repeatability and before/after comparison;
- recurring monitoring is a potential later product, but requires more infrastructure/support and should not distract from first WTP validation.

Sources:
- https://n8n.io/workflows/10852-automated-n8n-workflow-audit-and-export-tool-json-excel/
- https://n8n.io/workflows/16164-run-weekly-security-audits-via-the-n8n-api-data-tables-and-telegram/

## Strategic conclusions

### Keep
- local/privacy-first free preflight;
- evidence-first deterministic rules;
- fixed-scope EUR 149 paid audit;
- sample report;
- remediation + verification;
- no production credentials.

### Improve now
- professional website hierarchy and visual trust;
- explain "who this is for" in business terms;
- clearer free-vs-paid distinction;
- make the workflow visible: Export -> Local Preflight -> Audit -> Re-scan;
- show concrete risk classes rather than generic "automation quality";
- explicit "what PCFlows does not do" to increase credibility.

### Do not build yet
- continuous monitoring;
- Make API account connection;
- live incident response;
- generic AI chatbot analysis;
- broad n8n/Zapier support;
- health score gamification;
- operation-cost optimizer;
- implementation retainer.

### Candidate next product layer after WTP

**Sanitized Runtime Evidence Review**

Input:
- blueprint;
- one successful execution sample;
- one failed/suspicious execution sample;
- no credentials.

Potential output:
- structural finding + runtime evidence correlation;
- changed field/module diff;
- likely failure boundary;
- verification steps.

Gate: build only after real paid customers show that static blueprint analysis alone leaves repeated high-value questions unanswered.
