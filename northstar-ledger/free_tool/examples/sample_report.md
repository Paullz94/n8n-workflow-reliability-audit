# Northstar Preflight Lite Report

Version: 0.1.0
Files scanned: 2
Findings: 5 (critical 1, high 2, medium 0, low 2)

Heuristic preflight only; not a penetration test, security audit, compliance check, or production certification.

## [CRITICAL] Possible OpenAI secret committed
- Rule: SECRET-OPENAI
- Location: app.py:2
- Evidence: sk-pro…STUV

## [HIGH] Stripe usage found without obvious webhook signature verification
- Rule: STRIPE-WEBHOOK-VERIFY
- Location: .:1

## [HIGH] Debug mode appears enabled
- Rule: DEBUG-ENABLED
- Location: app.py:1
- Evidence: DEBUG=True

## [LOW] No GitHub Actions workflow detected
- Rule: CI-MISSING
- Location: .:1

## [LOW] No obvious automated tests detected
- Rule: TESTS-MISSING
- Location: .:1
