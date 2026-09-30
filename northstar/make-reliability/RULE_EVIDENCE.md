# Reliability Rule Evidence

Updated: 2026-09-25

PCFlows static checks should be tied to documented Make.com semantics whenever possible. This file records the primary source behind the current higher-consequence rules.

| PCFlows rule | Make behavior being reviewed | Primary reference |
|---|---|---|
| `write-skip-handler-data-loss-review` | Skip/Ignore drops the failed bundle and allows later bundles to continue; Make documents that the run can still be marked successful | https://help.make.com/skip-error-handler |
| `write-resume-handler-silent-success-review` | Resume replaces failed-module output with substitute data and continues downstream processing | https://help.make.com/resume-error-handler |
| `write-commit-partial-state-review` | Commit stops the run while preserving earlier transactional changes | https://help.make.com/commit-error-handler |
| `rollback-limited-by-autocommit-review` | Rollback cannot undo earlier changes already committed when auto-commit is enabled | https://help.make.com/rollback-error-handler |
| `auto-commit-recovery-review` | Auto-commit commits after each module, which can make earlier transactional changes irreversible after a later error | https://help.make.com/scenario-settings |
| `concurrency-review` | Instant webhooks are processed in parallel by default unless process-in-order behavior is enabled | https://help.make.com/webhooks |
| `incomplete-executions-disabled-review` | Incomplete executions are a recovery/data-loss safety feature and are disabled by default | https://help.make.com/incomplete-executions |
| `data-loss-enabled` | When incomplete-execution storage is unavailable/full and data loss is enabled, Make can continue scheduling while discarding the incomplete execution | https://help.make.com/errors-that-dont-create-incomplete-executions |
| `retrying-write-idempotency-review` | Retry handlers store/retry failed work; write-side idempotency must be reviewed separately because external side effects may already have occurred | https://help.make.com/error-handlers |

## Evidence policy

- A rule should describe only what static blueprint evidence supports.
- Official Make documentation is preferred over forum posts or third-party tutorials.
- Third-party blueprint examples may be used to confirm exported token names such as `builtin:Ignore`, but not to define product behavior when official documentation is available.
- A rule is a review signal, not proof that the scenario is defective.
- Report language must distinguish documented Make behavior from PCFlows' risk interpretation.
