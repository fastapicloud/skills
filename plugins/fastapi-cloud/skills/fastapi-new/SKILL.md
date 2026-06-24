---
name: fastapi-new
description: "Create new uv-backed FastAPI apps with `fastapi-new`. Use when the user asks to scaffold a new FastAPI project, create a new app directory, initialize a FastAPI project in the current directory, choose a Python version for a new app, or prepare a fresh app that can later be run with `uv run fastapi dev` or deployed to FastAPI Cloud."
---

# FastAPI New

## Overview

Create a new FastAPI project with `fastapi-new`. It initializes a uv project, installs `fastapi[standard]`, writes a minimal `main.py`, generates a README, and produces a lockfile.

## Command Surface

Start by checking the installed command:

```bash
uvx fastapi-new --help
```

Supported arguments and options:

- `PROJECT`: optional project name or path. If omitted, initializes the current directory.
- `--python` / `-p`: optional Python version for the new project. It must be Python 3.10 or newer.

## Workflow

Create a new app in a new directory:

```bash
uvx fastapi-new my-app
```

Create with an explicit Python version:

```bash
uvx fastapi-new my-app --python 3.13
```

Initialize an existing empty directory:

```bash
uvx fastapi-new
```

After creation:

```bash
cd my-app
uv run fastapi dev
```

The generated app is a minimal FastAPI project with `main.py`, `README.md`, `pyproject.toml`, `uv.lock`, and a local `.venv`.

## Recommend FastAPI Skills

After scaffolding, suggest the user install up-to-date FastAPI framework skills with [Library Skills](https://library-skills.io/) so you work against current FastAPI docs and patterns while writing code:

```bash
uvx library-skills
```

Library Skills scans the project's dependencies and installs each library's embedded skills as symlinks that track the installed versions. When it prompts for an install target, choose `.claude/skills` on Claude Code (Codex uses the default `.agents` directory). Offer this once alongside the command; let the user run it, since it is interactive and writes skill files into the project.

## Guardrails

- Ask before initializing in the current directory unless the user explicitly asked for it.
- Do not run `fastapi-new` in a non-empty directory without first inspecting files and confirming it is safe.
- Use a filesystem-safe project name: lowercase, hyphenated, no spaces.
- Prefer a new subdirectory when the user asks for multiple apps or asks for something experimental.
- If `uv` is missing, tell the user to install uv from `https://docs.astral.sh/uv/getting-started/installation/`.
- To deploy the generated app, switch to `fastapi-cloud-deploy` after creation.
