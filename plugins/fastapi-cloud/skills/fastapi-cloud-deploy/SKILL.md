---
name: fastapi-cloud-deploy
description: "Prepare and deploy FastAPI apps to FastAPI Cloud. Use when the user asks to deploy a project, create or link a FastAPI Cloud app, log in before deployment, validate deployment inputs, inspect app IDs, review `.fastapicloudignore`, or update commands that invoke `fastapi deploy` or `fastapi cloud deploy`."
metadata:
  display_name: "FastAPI Cloud Deploy"
---

# FastAPI Cloud Deploy

## Overview

Deploy a local FastAPI project to FastAPI Cloud.

## CLI Baseline

Assume the released project CLI is correct and start with the `fastapi cloud ...` command needed for the task, such as:

```bash
uv run fastapi cloud deploy --help
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

If there is no project environment, create a temporary uv project and install the same dependency constraints before checking the command surface.

If the project cloud CLI reports a version older than `0.20.0`, update the project environment before retrying.

## JSON Output

Use `--json` whenever the command supports it. If command output includes terminal control sequences before the JSON payload, strip ANSI/OSC control sequences before parsing.

## Workflow

Inspect the project:

```bash
rg --files -g 'pyproject.toml' -g '.fastapicloud/**' -g '.fastapicloudignore' -g '.gitignore'
uv run fastapi cloud deploy --help
```

Check auth and linked app state:

```bash
uv run fastapi cloud whoami --json
uv run fastapi cloud apps get --json
```

If auth is missing or stale, ask before starting the login flow. If the project is not linked, inspect apps first; create or link only when the user asks.

## Authentication

Prefer the JSON device flow over plain `login` output:

```bash
uv run fastapi cloud auth login --no-open --json
```

Surface the returned `verification_uri_complete` or `verification_uri` plus `user_code` to the user. Then wait with the returned `device_code`:

```bash
uv run fastapi cloud auth wait --device-code DEVICE_CODE --interval 5 --timeout 300 --json
```

Deploy only after the user has requested deployment:

```bash
uv run fastapi cloud deploy . --json
```

Use `--app-id APP_ID` or `FASTAPI_CLOUD_APP_ID` for a specific target. `--json` deploy output implies non-waiting behavior; for non-JSON deploy commands, use `--no-wait` only when the user wants the command to return before the deployment reaches a terminal state.

## App Creation And Linking

Use read commands before write commands:

```bash
uv run fastapi cloud teams list --json
uv run fastapi cloud apps list --team-id TEAM_ID --json
uv run fastapi cloud apps create --team-id TEAM_ID --name APP_NAME --directory . --link --path . --json
uv run fastapi cloud link APP_ID --path . --json
```

`link` writes `.fastapicloud/cloud.json`; use `--force` only when replacing a known stale link.

## Deployment Inputs

- Ensure the project has a `pyproject.toml` with FastAPI dependencies.
- Inspect `.fastapicloudignore` and `.gitignore` before deploy if large files or secrets may be included.
- Keep access tokens in environment variables or CI secrets, not source files. App IDs may be passed explicitly with `--app-id` when needed.
- After deploy, report the deployment ID/status and next diagnostic command if available.
