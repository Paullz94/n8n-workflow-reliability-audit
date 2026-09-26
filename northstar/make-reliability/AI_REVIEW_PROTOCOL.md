# AI-Assisted Review Protocol

Updated: 2026-09-25

## Why this exists

Current competing reliability tools show a useful pattern: deterministic checks provide repeatability, while AI can help interpret ambiguous edge cases and communicate risk in business terms.

PCFlows will use that pattern conservatively:

> **Deterministic evidence first. AI interpretation second.**

AI is not allowed to manufacture new findings that have no evidence.

## Input boundary

Use `ai_review_packet.py` to create the only packet intended for AI-assisted interpretation.

The packet contains:
- allowlisted non-sensitive context;
- finding rule/severity/module type/path;
- deterministic evidence text;
- deterministic impact/action/verification;
- official Make reference where available.

It excludes:
- raw blueprint JSON;
- mapper/parameter values;
- credentials;
- customer records.

If secret detection fires, packet generation hard-stops.

## AI output contract

The model may:
- prioritize the supplied findings;
- explain business consequences conditionally;
- point out ambiguity;
- propose safe synthetic verification;
- improve client-facing clarity;
- identify where runtime evidence would be needed.

The model must not:
- invent a production incident;
- state that a static signal proves a defect;
- infer credentials, live configuration or customer data;
- request production secrets;
- replace deterministic findings with a free-form score;
- make compliance/security certification claims.

## Review sequence

1. Deterministic scan.
2. Secret gate.
3. Deterministic paid report.
4. AI review packet.
5. AI-assisted interpretation using the packet only.
6. Compare AI interpretation back to deterministic evidence.
7. Human/agent QA: remove any unsupported claim.
8. Deliver final bounded report.

## Product positioning

PCFlows should not advertise "AI found X" as the primary value.

Preferred framing:
- evidence-first;
- Make-specific;
- deterministic checks;
- AI-assisted prioritization/clarity when useful;
- explicit limitations.

## Expansion gate

Do not build a paid external LLM/API dependency during the EUR 0 / early-revenue phase.

Use already-available reasoning capacity where permitted. Reconsider a dedicated model/API only if real customer volume proves that:
- AI interpretation materially improves conversion/delivery quality;
- the cost per order is measured;
- business-generated revenue can fund it;
- privacy terms remain appropriate.
