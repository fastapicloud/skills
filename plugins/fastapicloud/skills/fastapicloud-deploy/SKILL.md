---
name: fastapicloud-deploy
description: "Prepare and deploy FastAPI apps to FastAPI Cloud. Use when the user asks to deploy a project, create, link, or update a FastAPI Cloud app, log in before deployment, set up CI/CD, a GitHub Actions deploy workflow, or GitHub-linked auto-deploys, manage deploy tokens, validate deployment inputs, inspect app IDs, review `.fastapicloudignore`, or update commands that invoke `fastapi deploy` or `fastapi cloud deploy`."
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

If the project cloud CLI reports a version older than `0.21.0`, update the project environment before retrying.

## JSON Output

Use `--json` whenever the command supports it. Parse stdout directly as the CLI's structured JSON envelope; treat other stdout as an incompatible or stale command surface.

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

## App Creation, Linking, And Updates

Use read commands before write commands:

```bash
uv run fastapi cloud teams list --json
uv run fastapi cloud apps list --team-id TEAM_ID --json
uv run fastapi cloud apps create --team-id TEAM_ID --name APP_NAME --link --path . --json
uv run fastapi cloud link APP_ID --path . --json
```

For a monorepo app, pass `--directory DIRECTORY` to `apps create`. This is the app's relative directory containing `pyproject.toml`; `--path` is the local directory where linking writes configuration.

Read the app before changing its configured directory. `apps update` requires CLI `0.22.0` or newer:

```bash
uv run fastapi cloud apps get APP_ID --json
uv run fastapi cloud apps update APP_ID --directory DIRECTORY --json
```

Only update app metadata when the user asks. `link` writes `.fastapicloud/cloud.json`; use `--force` only when replacing a known stale link.

## CI And Deploy Tokens

For non-interactive deploys (CI/CD), authenticate with a deploy token instead of the device flow. These commands require CLI `0.21.0` or newer. Read before mutating:

```bash
uv run fastapi cloud tokens list --app-id APP_ID --json
```

Create or delete tokens only when the user asks. `tokens create` returns the secret value once — write it to a file with `--output-file` or capture it directly into a CI secret; never echo it in chat or shell history. Use `--expires-in-days N` to bound its lifetime:

```bash
uv run fastapi cloud tokens create --app-id APP_ID --name NAME --output-file PATH --json
uv run fastapi cloud tokens delete TOKEN_ID --app-id APP_ID --json
```

### GitHub Actions

Preview the generated workflow first; `print-workflow` is read-only and writes no files or secrets:

```bash
uv run fastapi cloud ci print-workflow --json
uv run fastapi cloud ci print-workflow --branch BRANCH
```

`ci setup` is a mutating convenience: it writes `.github/workflows/deploy.yml` and sets the `FASTAPI_CLOUD_TOKEN` and `FASTAPI_CLOUD_APP_ID` GitHub Actions secrets via the `gh` CLI (creating a deploy token in the process). Run it only when the user asks; first confirm `git` and `gh` are installed and the repo has an `origin` remote, then surface what it will change:

```bash
uv run fastapi cloud ci setup
```

FastAPI Cloud also supports native GitHub deployments — linking a repository so pushes deploy automatically. This is not available through the CLI yet; tell the user to set it up from their app's settings in the FastAPI Cloud dashboard.

## Deployment Inputs

- Ensure the project has a `pyproject.toml` with FastAPI dependencies.
- Inspect `.fastapicloudignore` and `.gitignore` before deploy if large files or secrets may be included.
- Keep access tokens in environment variables or CI secrets, not source files. App IDs may be passed explicitly with `--app-id` when needed.
- After deploy, report the deployment ID/status and next diagnostic command if available.
