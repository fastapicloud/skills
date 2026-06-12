---
name: fastapi-cloud-logs
description: "Inspect FastAPI Cloud logs. Use when the user asks for recent logs, the latest or last log timestamp, runtime log lines, build logs for a deployment, whether an app has emitted logs, or a quick app log/health check."
---

# FastAPI Cloud Logs

## Overview

Inspect FastAPI Cloud logs with the narrowest read-only command that answers the user. Prefer direct log retrieval over broad deployment debugging unless the log output points to a failure that needs deeper triage.

## Command Baseline

Confirm log flags only when needed:

```bash
uv run fastapi cloud logs --help
```

Use `uv run fastapi cloud apps get --json` only when resolving the linked current directory. Use `--json` whenever the command supports it.

## App Resolution

Resolve the app only as far as needed:

1. Use an explicit app ID, app slug, path, or deployment ID from the user.
2. Use the linked current directory with `uv run fastapi cloud apps get --json`.
3. Use `--app-id APP_ID` when the directory is not linked but an app ID is known.
4. List teams and apps only when the user did not provide an app and the local link cannot resolve one.

Do not create apps, link directories, deploy, or mutate environment variables while answering a log request unless the user explicitly asks.

## Runtime Logs

For recent runtime logs:

```bash
uv run fastapi cloud logs . --no-follow --tail 100 --since 30m --json
uv run fastapi cloud logs --app-id APP_ID --no-follow --tail 100 --since 30m --json
```

For the latest log timestamp, try the narrowest command first:

```bash
uv run fastapi cloud logs . --no-follow --tail 1 --json
uv run fastapi cloud logs --app-id APP_ID --no-follow --tail 1 --json
```

If the command returns no lines or requires a time window, widen with bounded supported ranges such as `30m`, `24h`, `7d`, then `30d`. Do not use very large ranges such as `365d`; report the widest window checked when no logs are found.

## Build Logs

When the user asks for build logs or names a deployment:

```bash
uv run fastapi cloud deployments list --app-id APP_ID --json
uv run fastapi cloud deployments build-logs DEPLOYMENT_ID --no-follow --json
```

If no deployment ID is provided, use the newest deployment from `deployments list`.

## Authentication

Treat auth as a blocker, not the main workflow:

- If a read command returns `not_logged_in` or `invalid_token`, stop and tell the user authentication is blocking the log request.
- Ask before starting the device login flow.
- After approval, use the JSON device flow:

```bash
uv run fastapi cloud auth login --no-open --json
uv run fastapi cloud auth wait --device-code DEVICE_CODE --interval 5 --timeout 300 --json
```

Surface only the login URL or user code needed for authorization. Do not print token values, ask the user to paste tokens, or inspect `FASTAPI_CLOUD_TOKEN` unless the user is debugging CI/auth configuration.

## Response

Answer the concrete log question first: newest timestamp, matching log lines, empty result, or the auth/app-resolution blocker. Include the app name or ID only when it clarifies the evidence, and keep follow-up diagnostics to the next likely command.
