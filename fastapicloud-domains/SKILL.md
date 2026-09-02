---
name: fastapicloud-domains
description: "Manage custom domains for FastAPI Cloud apps. Use when listing or inspecting domains, adding a hostname, choosing standard or zero-downtime DNS setup, checking verification or TLS progress, restarting failed setup, or removing a custom domain."
---

# FastAPI Cloud Domains

## Overview

Add, inspect, troubleshoot, and remove custom domains for a FastAPI Cloud app. The CLI reports the DNS records the user must configure; it does not change records at the user's DNS provider.

## CLI Baseline

Custom domain commands require FastAPI Cloud CLI `0.25.0` or newer. Start with the command needed for the task:

```bash
uv run fastapi cloud domains --help
```

Only check the version if the `domains` command is missing or incompatible:

```bash
uv run fastapi cloud --version
```

If an update is needed, ask before changing an existing project environment, then update `fastapi[standard]` rather than installing `fastapi-cli` directly:

```bash
uv add -U "fastapi[standard]"
uv lock --upgrade-package fastapi --upgrade-package fastapi-cloud-cli
```

## Authentication And App Resolution

Domain management requires a logged-in user session; a deploy token is only for deployments and CI. If authentication fails, report the blocker and ask before starting the JSON device flow:

```bash
uv run fastapi cloud auth login --no-open --json
uv run fastapi cloud auth wait --device-code DEVICE_CODE --interval 5 --timeout 300 --json
```

Use an explicit `--app-id APP_ID` when the user provides one. Otherwise use the app linked to the current directory. Resolve an uncertain target with read commands before making changes:

```bash
uv run fastapi cloud apps get --json
uv run fastapi cloud domains list --app-id APP_ID --json
```

Use `--json` whenever supported. JSON mode is non-interactive, so provide every required domain, setup mode, and confirmation flag explicitly.

## Inspect Domains

List an app's custom domains before selecting one:

```bash
uv run fastapi cloud domains list --app-id APP_ID --json
```

Inspect one domain by hostname or domain ID:

```bash
uv run fastapi cloud domains get DOMAIN --app-id APP_ID --json
```

`domains get` reports setup status, the DNS records currently required, and the live HTTPS URL after setup succeeds. In JSON mode, `DOMAIN` is required. Use the exact record type, name, and value returned by the CLI; do not infer DNS records from other apps or domains.

## Add A Domain

First determine whether the hostname is new or already serves production traffic. If this is unclear, ask—the choice changes the DNS workflow.

For a new or unused hostname, use standard setup:

```bash
uv run fastapi cloud domains add DOMAIN --app-id APP_ID --standard --json
```

For an already-live hostname, use zero-downtime setup:

```bash
uv run fastapi cloud domains add DOMAIN --app-id APP_ID --zero-downtime --json
```

`--standard` and `--zero-downtime` are mutually exclusive. JSON mode requires `DOMAIN` and one setup mode.

- Standard setup returns the records used to verify ownership, issue TLS, and route traffic.
- Zero-downtime setup proceeds in phases: prove ownership, secure the domain, then switch traffic. Only configure the records currently shown by `domains get`; later records unlock as verification advances.

After the user updates DNS, check progress with:

```bash
uv run fastapi cloud domains get DOMAIN --app-id APP_ID --json
```

FastAPI Cloud rechecks pending or mismatched records automatically. Do not restart setup merely because DNS is still propagating.

## Restart Failed Setup

Restart only after `domains get` reports a failed setup and the returned DNS records have been checked or corrected:

```bash
uv run fastapi cloud domains restart DOMAIN --app-id APP_ID --json
uv run fastapi cloud domains get DOMAIN --app-id APP_ID --json
```

In interactive mode, omitting `DOMAIN` offers only failed domains. In JSON mode, `DOMAIN` is required.

## Remove A Domain

Inspect the exact domain first and explain the effect. Removal deletes FastAPI Cloud's resources for the domain but does not change DNS records at the provider.

```bash
uv run fastapi cloud domains get DOMAIN --app-id APP_ID --json
uv run fastapi cloud domains remove DOMAIN --app-id APP_ID --yes --json
```

Only remove a domain when the user explicitly asks. JSON mode requires both `DOMAIN` and `--yes`. After removal, remind the user to review stale DNS records at their provider; do not claim those records were deleted.

## Response

Report the app and hostname affected, the resulting setup status, and the next required DNS action. For setup in progress, include only the currently required records and the next `domains get` command. Never claim a domain is live until the CLI reports successful setup.
