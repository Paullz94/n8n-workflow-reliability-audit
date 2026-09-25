# One-Time Make MCP Prerequisite — PCFlows

Prepared: 2026-09-25

This prerequisite is needed only for future connected runtime verification / Verified Repair.
The audit packages do not need it.

## Current official route

Make released an official ChatGPT plugin on 2026-09-09.

Make says it supports building, running, reviewing and managing Make automations from ChatGPT.

Official:
https://help.make.com/official-make-plugin-for-chatgpt-is-now-available

## Preferred setup

### Option A — official Make plugin
If Make appears in ChatGPT's plugin directory for Paul's account:
1. Settings -> Plugins.
2. Find the official Make plugin.
3. Connect the dedicated PCFlows Make identity/account.
4. Grant only the capabilities required for the PCFlows runtime workflow.

### Option B — MCP toolbox (preferred restricted fallback)
If the official plugin is not surfaced in the current directory:

In Make:
1. Open **MCP Toolboxes**.
2. Create a toolbox named **PCFlows Verification**.
3. Add only active on-demand scenarios designed for PCFlows synthetic verification.
4. Mark read-only tools read-only and write tools read/write accurately.
5. Create a dedicated toolbox key.
6. Copy the toolbox MCP Server URL.

In ChatGPT web:
1. Settings -> Plugins.
2. Enable Developer mode.
3. Browse plugins -> + Add custom MCP server.
4. Name it **PCFlows Make Verification**.
5. Connection URL:
   `<MCP TOOLBOX URL>/t/<TOOLBOX KEY>/stateless`
6. Authentication: No Auth, because the toolbox key is embedded in the URL format documented by Make.
7. Create and Connect.

Make recommends stateless Streamable HTTP for reliability.

Official instructions:
https://help.make.com/connect-to-chatgpt
https://help.make.com/mcp-toolboxes

## Security

The toolbox key is a credential.

Paul should enter it directly in the ChatGPT connection UI.
Do **not** paste it into this conversation.
Do **not** commit it to GitHub.
Do **not** email it.

## Toolbox limitation

Make documents a 40-second toolbox execution timeout.

PCFlows test-tool scenarios should therefore:
- use small synthetic inputs;
- return one compact proof object;
- normally finish well below 40 seconds;
- move longer asynchronous verification to another bounded mechanism if necessary.

## After connection

Once Make appears as a connected tool in ChatGPT, PCFlows can begin the real integration gate:
- inspect available Make tools;
- create/verify a PCFlows sandbox;
- exercise run/replay;
- test backup/update/rollback;
- run one end-to-end synthetic repair;
- only then consider enabling Verified Repair publicly.

No ChatGPT Work setup is required for this connection.
