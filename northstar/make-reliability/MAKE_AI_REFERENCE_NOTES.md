# Make AI Reference Notes — Inputs for PCFlows

Research date: 2026-09-25

Primary source:
https://github.com/integromat/make-skills

Make publishes an MIT-licensed skill set for AI coding agents (Claude Code, Codex and other agent systems). These notes capture reliability/safety implications useful to PCFlows without turning the audit into a scenario-building service.

## Confirmed blueprint/error tokens

Make's blueprint-construction guidance documents the canonical directives:
- builtin:Resume
- builtin:Commit
- builtin:Rollback
- builtin:Ignore
- builtin:Break

This validates the exact tokens PCFlows scans rather than relying on guessed names.

Source:
https://github.com/integromat/make-skills/blob/main/skills/make-scenario-building/blueprint-construction.md

## Error-handler semantics

Make's AI skill documents:
- Break: incomplete execution / retry path;
- Commit: stop while preserving prior changes;
- Ignore: discard the error and continue subsequent bundles;
- Resume: substitute fallback output and continue;
- Rollback: undo changes only for transaction-capable modules.

Reliability implication:
The presence of an error handler is not enough to call a scenario "safe". The specific directive changes data-loss, silent-success and recovery behavior.

Source:
https://github.com/integromat/make-skills/blob/main/skills/make-scenario-building/error-handling.md

## Rollback is not universal

Make's AI guidance explicitly notes that Rollback works only for modules that support transactions/ACID behavior. Non-transactional external effects cannot necessarily be undone.

PCFlows implication:
- current Rollback checks remain review signals;
- do not promise "all-or-nothing" merely because a Rollback directive exists;
- a future richer audit could use Make module metadata to identify transaction-capable modules, but that would require a new trusted data source/API and is outside the current zero-credential pilot.

## Success status is not business correctness

Make's blueprint guidance explicitly warns that a successful execution status means nothing crashed, not that the output is correct. It recommends explicit validation/Throw patterns for output contracts in scenarios that can otherwise return empty/malformed data.

PCFlows implication:
- current product framing "green can still be wrong" is technically aligned with Make's own AI guidance;
- static findings must continue to distinguish platform success from business success;
- do not infer a live failure from a static blueprint.

## Webhook URL is a credential

Make's webhook skill states that the webhook URL acts as address/authentication and should not be exposed publicly without additional protection.

PCFlows action:
- Make webhook URLs are now part of the secret-like detector;
- paid fulfillment hard-stops until the customer supplies a re-sanitized file;
- public guidance should explicitly mention private webhook URLs alongside API keys/passwords.

Sources:
- https://github.com/integromat/make-skills/blob/main/skills/make-scenario-building/webhooks.md
- https://apps.make.com/gateway

## Parallel webhook execution

Make's AI guidance confirms webhook scenarios process requests in parallel by default unless sequential processing is enabled.

PCFlows action:
- concurrency-review remains a core data-integrity rule where writes are present;
- business context determines whether ordering matters.

## Module validation

Make's module-configuring skill strongly prefers interface-driven validation rather than guessing parameters.

Future implication:
If PCFlows ever adds an opt-in implementation or repair tier, it should use Make's own module validation/MCP primitives rather than inventing module parameter schemas.

Current decision:
Do not add implementation/repair to the EUR 149 pilot.

## Product boundary learned from official AI guidance

Make's own AI skills are primarily about **building and changing** scenarios.
PCFlows should stay on the other side of that boundary for the pilot:
- inspect;
- explain;
- prioritize;
- verify;
- re-scan.

That preserves a productized audit instead of becoming another general automation agent.
