# PCFlows Make Access Model for Verified Repair

Research date: 2026-09-25
Status: design prepared; no customer Make access is currently connected.

## Goal

Verified Repair must not require a customer to email or paste a Make API token, webhook secret, app password, or production credential.

The preferred access model is **delegated team membership for a PCFlows service identity**.

## Why this is viable

Make teams own:
- scenarios;
- connections;
- webhooks;
- keys;
- data stores;
- other team resources.

Make documents that a user can belong to multiple organizations and teams, with different roles in each team.

Default team roles include:
- Team Member — broad editing access to team resources;
- Team Operator — read-only resources but can activate/deactivate/schedule scenarios;
- Team Monitoring — read-only monitoring;
- Team Guest — credential-request-specific access only.

For repair, Team Operator is insufficient because it cannot edit scenarios. A normal Team Member can edit, but has broader access than PCFlows ideally needs.

Official source:
https://help.make.com/teams

## Preferred customer setup

### Audit-only customer
No Make account access.

Customer supplies:
- sanitized blueprint;
- non-sensitive context.

### Verified Repair customer
Preferred workflow:

1. Customer creates or designates the smallest possible Make team for the repair.
2. Only the target/test scenarios and required test connections should be present when practical.
3. Customer invites the PCFlows service identity to that team for the repair period.
4. PCFlows uses its own service identity/API authorization.
5. Customer never shares their own API token or app credentials with PCFlows.
6. PCFlows performs diagnosis/repair/testing according to the resolution contract.
7. After completion, customer can remove the PCFlows user from the team.

For Enterprise customers, a custom role may allow tighter least-privilege permissions.

## Production vs test

A customer production team is not automatically an acceptable runtime test environment.

For high-impact writes:
- prefer a cloned scenario;
- map to test/sandbox app connections;
- use synthetic records;
- explicitly identify the natural business key;
- ensure side effects can be counted/verified;
- only deploy the validated blueprint to production after test acceptance criteria pass.

Make's Clone Scenario API supports mapping entity IDs when cloning to another team; Make warns that app connections/webhooks/data stores need mapping or configuration review.

Official source:
https://developers.make.com/api-documentation/api-reference/scenarios

## Service identity

A dedicated PCFlows Make account should eventually be created rather than using Paul's personal Make identity.

Public/customer support identity:
PCFlows

Admin support mailbox:
PCMotionstudios@gmail.com

A dedicated Make service account address can be chosen later if separation is useful.

## Token model

PCFlows's Make API token:
- belongs to the PCFlows service identity;
- stored only in a secure runtime secret/connector;
- never committed to GitHub;
- never sent in email/chat;
- must have only the scopes required by the enabled feature.

Runtime verification needs:
- scenarios:read
- scenarios:run

Automated repair/deployment additionally needs:
- scenarios:write

Official scope reference:
https://developers.make.com/api-documentation/authentication/api-scopes-overview

## Activation prerequisite

Before Verified Repair can launch, Paul must perform one one-time infrastructure setup:
- create/choose the dedicated PCFlows Make service identity;
- create secure API/MCP authorization with the minimum required scopes;
- connect that authorization to the PCFlows runtime.

This is an account/security prerequisite, not a daily operator task.

## Customer access automation

After the service identity exists, customer onboarding can be autonomous:
- PCFlows sends exact invite instructions;
- customer performs the invitation;
- PCFlows detects when access becomes available;
- repair starts automatically;
- PCFlows can instruct removal after case closure.

## Hard safety rules

- Never ask the customer to email their Make token.
- Never ask the customer to send production connection credentials.
- Never run destructive verification against real customer records when a synthetic test is possible.
- Never call a repair complete until every resolution contract is closed_verified.
- Do not keep access longer than needed for the defined service.


## Preferred ChatGPT integration — official Make MCP

Research update: 2026-09-25

Make now provides an official Make plugin / MCP integration for ChatGPT.

Make states that the ChatGPT integration can:
- describe/build Make automations;
- run scenarios;
- review output;
- search/manage automations and execution history;
- continue using connections and governance stored inside Make.

Official sources:
- https://help.make.com/official-make-plugin-for-chatgpt-is-now-available
- https://help.make.com/connect-to-chatgpt
- https://help.make.com/make-mcp-server

### Preferred PCFlows architecture

Use the official Make MCP path before inventing a custom hosted bridge.

There are two relevant Make MCP options:

1. **Make MCP server**
   - broad account management/run access;
   - quickest connection;
   - less granular scenario restriction.

2. **MCP toolbox**
   - exposes a specific selected set of active, on-demand scenarios as tools;
   - unique URL and key;
   - multiple keys;
   - read-only/read-write annotations;
   - preferable for tightly controlled PCFlows test tools.

Official toolbox source:
https://help.make.com/mcp-toolboxes

### ChatGPT connection without Work

Make documents connecting an MCP toolbox directly to normal ChatGPT:
- ChatGPT web -> Settings -> Plugins -> Developer mode;
- add custom MCP server;
- use the Make toolbox URL plus toolbox key;
- stateless Streamable HTTP is recommended.

This does not require ChatGPT Work as the browser operator.

### Current recommendation

For PCFlows Verified Repair:
- use the official Make plugin/MCP server for Make account/scenario management where the necessary tools/scopes are exposed;
- use a dedicated **PCFlows Verification Toolbox** for narrowly scoped synthetic acceptance-test scenarios;
- keep production writes additionally protected by PCFlows case/customer authorization and allowlists.

### Current status

The official Make plugin/MCP connection exists as a supported product, but it is **not connected to this ChatGPT session yet**.

Plugin directory search through the currently connected plugin-management interface did not surface Make even though Make's current official documentation says it is available. The documented custom-MCP toolbox route is therefore the deterministic fallback connection path.
