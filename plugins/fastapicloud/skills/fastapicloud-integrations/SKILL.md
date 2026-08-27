---
name: fastapicloud-integrations
description: "Connect and manage databases and third-party resources for FastAPI Cloud apps. Use when the user asks to connect or add a database, Postgres provider, Redis cache, observability service, or other managed service; inspect available integration providers; connect Neon, Redis Cloud, Supabase, or Logfire; list or inspect connected resources; review managed environment variables; or disconnect a resource from an app."
---

# FastAPI Cloud Integrations

## Overview

Inspect available providers and manage resources connected to a FastAPI Cloud app. Current providers include Neon, Redis Cloud, Supabase, and Logfire; use the CLI provider list as the source of truth for availability.

Treat the connected resource as the integration abstraction. Current integrations configure the app through managed environment variables, but do not define integrations as env-var management alone: future providers may add other behavior and metadata. Follow the current CLI response rather than assuming environment variables are the complete integration contract.

## CLI Baseline

Start with the command needed for the task:

```bash
uv run fastapi cloud integrations --help
```

Only check the CLI version after the command is missing or reports an incompatible command surface:

```bash
uv run fastapi cloud --version
uv run fastapi cloud integrations --help
```

Integration commands require FastAPI Cloud CLI `0.24.0` or newer. If the project CLI is older, ask before updating the existing project environment:

```bash
uv add -U "fastapi[standard]"
uv lock --upgrade-package fastapi --upgrade-package fastapi-cloud-cli
```

Install or update `fastapi[standard]`, not `fastapi-cli` directly. The standard FastAPI extra provides the `fastapi` command and FastAPI Cloud CLI integration.

## JSON Output

Use `--json` whenever the command supports it. JSON mode is non-interactive: resolve required team, app, and resource IDs before running a mutating command.

## Resolve The Target

Prefer the narrowest available scope:

1. Use an explicit team, app, or resource ID supplied by the user.
2. Use the app linked to the current directory when it is the intended target.
3. Read teams, apps, providers, or connected resources only as needed to resolve a missing ID.

Useful read commands:

```bash
uv run fastapi cloud apps get --json
uv run fastapi cloud teams list --json
uv run fastapi cloud apps list --team-id TEAM_ID --json
```

Do not create or link an app, deploy code, or change environment variables merely to answer an integration query.

## Database And Service Requests

When the user asks to connect a database or another external service, check FastAPI Cloud integrations before proposing manual credentials or environment variables:

1. Resolve the intended FastAPI Cloud app and team.
2. List integration providers for that team.
3. Match the requested capability to providers reported as available or connected.
4. If multiple providers fit a generic request such as PostgreSQL, show the supported choices and ask which one the user wants.
5. Use the resource connection flow when a supported provider is selected.
6. If no integration supports the request, explain that clearly before offering manual environment-variable configuration.

Do not assume a service is unsupported from the static provider examples in this skill. Always use `integrations providers list` when the CLI is available. Do not manually set provider credentials when a supported managed integration is appropriate unless the user explicitly prefers manual configuration.

## Providers

List providers and their connection status for the linked app's team:

```bash
uv run fastapi cloud integrations providers list --json
```

Use an explicit team when the current directory is not linked or the user selected another team:

```bash
uv run fastapi cloud integrations providers list --team-id TEAM_ID --json
```

Treat provider status from this response as authoritative. A provider can be available, connected, or coming soon.

## Connected Resources

List resources connected to the linked app or a specific app:

```bash
uv run fastapi cloud integrations resources list --json
uv run fastapi cloud integrations resources list --app-id APP_ID --json
```

Inspect one resource after resolving its ID from the list:

```bash
uv run fastapi cloud integrations resources get RESOURCE_ID --json
uv run fastapi cloud integrations resources get RESOURCE_ID --app-id APP_ID --json
```

The resource details include provider metadata, a provider console URL, and managed environment variable names. Do not claim the CLI reveals environment variable values.

## Connect A Resource

Connecting a provider resource is completed in the FastAPI Cloud dashboard. In JSON mode, the CLI does not open a browser; it returns a `connect_url` to surface to the user:

```bash
uv run fastapi cloud integrations resources connect --json
uv run fastapi cloud integrations resources connect --app-id APP_ID --json
```

Do not claim the connection is complete merely because the URL was generated. Let the user finish provider selection and authorization in the browser, then verify with:

```bash
uv run fastapi cloud integrations resources list --app-id APP_ID --json
```

## Disconnect A Resource

Read the resource first and explain the effect before disconnecting it. Disconnecting removes the resource's managed environment variables from the FastAPI Cloud app, but does not delete the resource from Neon, Redis Cloud, Supabase, or Logfire.

Only disconnect when the user explicitly asks. JSON mode requires both the resource ID and confirmation:

```bash
uv run fastapi cloud integrations resources get RESOURCE_ID --app-id APP_ID --json
uv run fastapi cloud integrations resources disconnect RESOURCE_ID --app-id APP_ID --yes --json
```

Report the disconnected resource ID and any managed environment variable names removed from the app. Never substitute a similarly named resource without confirming its ID.

## Authentication

If a read command returns `not_logged_in` or `invalid_token`, stop and report the blocker. Ask before starting login. After approval, use the JSON device flow:

```bash
uv run fastapi cloud auth login --no-open --json
uv run fastapi cloud auth wait --device-code DEVICE_CODE --interval 5 --timeout 300 --json
```

Surface only the verification URL and user code needed for authorization. Never print or request token values.
