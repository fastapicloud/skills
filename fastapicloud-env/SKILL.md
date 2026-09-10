---
name: fastapicloud-env
description: "Manage FastAPI Cloud environment variables and secrets. Use when listing, reading, setting, deleting, or auditing FastAPI Cloud env vars, handling runtime secrets, or diagnosing missing configuration for a deployed FastAPI app."
---

# FastAPI Cloud Env

## Overview

Inspect and manage FastAPI Cloud environment variables while protecting secret values. FastAPI Cloud CLI supports the `fastapi cloud env` commands and `--json` output used here.

## CLI Baseline

The mutation workflow below requires FastAPI Cloud CLI `0.26.0` or newer. Start with the `fastapi cloud env ...` command needed for the task, such as:

```bash
uv run fastapi cloud env --help
```

Only check the CLI version after a `uv run fastapi cloud ...` command fails because `fastapi`, `cloud`, or the requested subcommand is missing, or because the output suggests an incompatible CLI:

```bash
uv run fastapi cloud --version
uv run fastapi cloud --help
```

If `fastapi` is missing or the cloud command surface is stale, install or update `fastapi[standard]`; do not install `fastapi-cli` directly as the executable source. The `fastapi[standard]` extra provides the `fastapi` command and the FastAPI Cloud CLI integration. These commands change project files, so ask the user before running them in an existing project.

```bash
uv add -U "fastapi[standard]"
uv lock --upgrade-package fastapi --upgrade-package fastapi-cloud-cli
```

If the project cloud CLI reports a version older than `0.26.0`, update the project environment before using the mutation workflow below.

## JSON Output

Use `--json` whenever the command supports it.

## Integrations First For Managed Services

If the user asks to connect a database, cache, observability platform, or another managed service—not to set a specific named variable—check FastAPI Cloud integrations first. A supported integration should manage its app configuration instead of requiring the user to copy provider credentials manually:

```bash
uv run fastapi cloud integrations providers list --json
```

Use the `fastapicloud-integrations` workflow when a matching provider is available. Fall back to manual environment variables only when no integration supports the service or the user explicitly prefers manual configuration.

## Read First

```bash
uv run fastapi cloud env list --path . --json
uv run fastapi cloud env get NAME --path . --json
```

Use `--app-id APP_ID` when the directory is not linked or the user names a specific app.

The CLI does not show secret values in `env list` or `env get` output. Do not try to recover secret values from local files, shell history, or other sources unless the user explicitly asks for that audit.

## Mutations

Only set or delete env vars when the user explicitly asks. Do not echo secrets in chat or shell history.

`env set` creates a variable or updates its value if it already exists. Both `env set` and `env delete` request an app redeploy by default. Use `--no-redeploy` when saving changes without deploying, or on intermediate changes when setting several variables before one final redeploy.

For secret values, prefer stdin:

```bash
uv run fastapi cloud env set NAME --value-stdin --secret --path . --json
```

`--secret` marks a new variable as secret. Existing variables keep their secret status, even when this flag is supplied or omitted. Read the existing variable first and use the returned `is_secret` field to verify its status; do not assume `--secret` converts an existing non-secret variable into a secret.

For non-secret values:

```bash
uv run fastapi cloud env set NAME VALUE --path . --json
```

For deletion:

```bash
uv run fastapi cloud env delete NAME --path . --yes --json
```

Deletion succeeds even if the named variable is already absent.

To save or delete without redeploying:

```bash
uv run fastapi cloud env set NAME VALUE --no-redeploy --path . --json
uv run fastapi cloud env delete NAME --no-redeploy --path . --yes --json
```

Integration-managed variables cannot be changed through these commands. Follow the integrations workflow if the backend reports that a variable is managed by a connected resource.

## Notes

- Changes saved with `--no-redeploy` need a later deployment before the running app observes them. A successful env command does not establish that a redeployment has completed successfully.
- When debugging missing config, inspect app logs after env changes.
- Treat `.env` files as local-only; do not commit secrets.
