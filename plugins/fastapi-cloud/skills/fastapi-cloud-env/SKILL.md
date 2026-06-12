---
name: fastapi-cloud-env
description: "Manage FastAPI Cloud environment variables and secrets. Use when listing, reading, setting, deleting, or auditing FastAPI Cloud env vars, handling runtime secrets, or diagnosing missing configuration for a deployed FastAPI app."
metadata:
  display_name: "FastAPI Cloud Env"
---

# FastAPI Cloud Env

## Overview

Inspect and manage FastAPI Cloud environment variables while protecting secret values. FastAPI Cloud CLI supports the `fastapi cloud env` commands and `--json` output used here.

## CLI Baseline

Assume the released project CLI is correct and start with the `fastapi cloud env ...` command needed for the task, such as:

```bash
uv run fastapi cloud env --help
```

Only check the CLI version after a `uv run fastapi cloud ...` command fails because `fastapi`, `cloud`, or the requested subcommand is missing, or because the output suggests an incompatible CLI:

```bash
uv run fastapi cloud --version
uv run fastapi cloud --help
```

If `fastapi` is missing or the cloud command surface is stale, install or update `fastapi[standard]`; do not install `fastapi-cli` directly as the executable source. The `fastapi[standard]` extra provides the `fastapi` command and the FastAPI Cloud CLI integration.

```bash
uv add -U "fastapi[standard]"
uv lock --upgrade-package fastapi --upgrade-package fastapi-cloud-cli
```

If the project cloud CLI reports a version older than `0.20.0`, update the project environment before retrying.

## JSON Output

Use `--json` whenever the command supports it.

## Read First

```bash
uv run fastapi cloud env list --path . --json
uv run fastapi cloud env get NAME --path . --json
```

Use `--app-id APP_ID` when the directory is not linked or the user names a specific app.

## Mutations

Only set or delete env vars when the user explicitly asks. Do not echo secrets in chat or shell history.

For secret values, prefer stdin:

```bash
uv run fastapi cloud env set NAME --value-stdin --secret --path . --json
```

For non-secret values:

```bash
uv run fastapi cloud env set NAME VALUE --path . --json
```

For deletion:

```bash
uv run fastapi cloud env delete NAME --path . --yes --json
```

## Notes

- Env var changes may require a redeploy or restart path before the running app observes them.
- When debugging missing config, inspect app logs after env changes.
- Treat `.env` files as local-only; do not commit secrets.
