# PCFlows Support Macros

Updated: 2026-09-25

These are internal starting points for one-to-one customer support. Personalize factual details before sending. Do not use them for bulk outreach.

## 1. Interest while checkout is paused

Subject: PCFlows Data Integrity Audit — launch update

Hello,

Thanks for your interest in the PCFlows Make.com Data Integrity Audit.

Paid checkout is temporarily paused while the Belgian business-registration setup is completed. Planned launch pricing is €0 for the local Reliability Preflight, €79 for a Focused Risk Check, €149 for the full Data Integrity Audit, and €399 for Portfolio / Release QA covering up to three related scenarios. In the meantime, you can already use the free local Reliability Preflight:

https://paullz94.github.io/n8n-workflow-reliability-audit/scanner.html

The core scan runs in your browser and does not require a Make.com API token.

Please do not send production credentials, passwords, API keys or private webhook secrets.

Regards,
PCFlows
PCMotionstudios@gmail.com

## 2. Paid order — files requested

Subject: PCFlows audit files — [STRIPE SESSION ID]

Hello,

Your PCFlows order is ready for intake.

Please send:
1. one sanitized Make.com scenario blueprint JSON;
2. the PCFlows intake JSON generated locally here:
   https://paullz94.github.io/n8n-workflow-reliability-audit/intake.html

Please keep the Stripe order reference in the subject.

Do not send:
- production credentials;
- passwords;
- API keys;
- private webhook secrets;
- customer records or unnecessary personal data.

Delivery starts after the usable sanitized input is received.

Regards,
PCFlows

## 3. Sanitization hard stop

Subject: PCFlows audit paused — please re-sanitize the blueprint

Hello,

PCFlows detected a possible secret-like literal in the supplied blueprint.

For privacy and safety, I have stopped the audit rather than continuing with that file.

Please:
1. remove or replace credentials, tokens, passwords and private webhook secrets;
2. rotate the value if you believe a real secret may have been exposed;
3. export/send a newly sanitized blueprint.

Do not email the secret itself.

Once the clean file is received, the audit can continue under the same order reference.

Regards,
PCFlows

## 4. Free preflight is sufficient

Subject: PCFlows preflight — deeper audit not necessary yet

Hello,

Based on the current sanitized blueprint and static findings, I do not see enough evidence to justify selling you the deeper EUR 149 review at this stage.

Keep the free preflight report and test the workflow with safe synthetic data.

A paid audit may become useful later if:
- the scenario handles business-critical writes;
- you see duplicate/missing/out-of-order results;
- error handlers or retries become difficult to reason about;
- you inherit a larger scenario with unclear recovery behavior.

This recommendation is based on static evidence only and is not a guarantee that the workflow is defect-free.

Regards,
PCFlows

## 5. Audit delivery

Subject: PCFlows Data Integrity Audit — [STRIPE SESSION ID]

Hello,

Your PCFlows Data Integrity Audit is attached.

The package contains:
- the prioritized audit report;
- machine-readable findings;
- the non-sensitive context used;
- an integrity manifest.

The raw blueprint is deliberately not included in the delivery ZIP.

Please start with the highest-severity findings, then use the verification steps with sanitized/synthetic test data.

The pilot includes one re-scan of the same scenario after remediation. Please request it within 30 calendar days of this delivery unless otherwise agreed.

Static analysis does not prove runtime correctness or the absence of defects.

Regards,
PCFlows

## 6. Re-scan received

Subject: PCFlows re-scan — [STRIPE SESSION ID]

Hello,

I received the revised sanitized blueprint for the included re-scan.

The comparison will classify deterministic findings as:
- statically cleared;
- remaining;
- new.

A finding disappearing from the revised blueprint means the static rule no longer matches. It does not by itself prove the runtime issue is fixed, so the original verification steps still matter.

Regards,
PCFlows

## 7. Re-scan delivery

Subject: PCFlows re-scan result — [STRIPE SESSION ID]

Hello,

Your included remediation re-scan is attached.

Please review:
- Statically cleared findings;
- Remaining findings;
- New findings.

A statically cleared finding means the revised blueprint no longer matches that deterministic rule. Runtime-dependent findings are not independently called fixed unless their required synthetic execution checks have been observed and passed.

This completes the included re-scan for this order.

Regards,
PCFlows

## 8. Out-of-scope cancellation / refund

Subject: PCFlows order — scope mismatch

Hello,

After reviewing the supplied material, this request falls outside the documented fixed-scope PCFlows Data Integrity Audit.

I will not expand the service silently into production implementation, unrestricted system access, incident response or another open-ended engagement.

Because the agreed audit cannot be performed within scope, I will follow the applicable cancellation/refund path for the order.

Regards,
PCFlows

## 9. Need more non-sensitive context

Subject: PCFlows audit — one clarification needed

Hello,

The blueprint is analyzable, but I need a small amount of non-sensitive context before prioritizing the findings.

Please use the local intake generator:
https://paullz94.github.io/n8n-workflow-reliability-audit/intake.html

It asks only for:
- scenario name;
- business goal;
- critical side effects;
- duplicate tolerance;
- whether ordering matters;
- recovery expectation.

Do not add credentials, customer data or secret values.

Regards,
PCFlows
