# FastAPI Cloud (Claude Code plugin)

Claude Code plugin for working with FastAPI Cloud from local FastAPI projects:
create apps, deploy, connect third-party resources, inspect logs, and manage
environment variables.

The Codex version of this plugin lives in a separate repository
(`fastapicloud/codex-plugins`); the two share the same `SKILL.md` instructions.

## FastAPI framework skills (Library Skills)

These skills handle deploying and operating apps on FastAPI Cloud. For help
*writing* FastAPI code, install the FastAPI framework skills with
[Library Skills](https://library-skills.io/): it scans your project's
dependencies and installs each library's embedded, always-up-to-date skills as
symlinks.

```bash
uvx library-skills        # Python projects (use `npx library-skills` for JS/TS)
```

When prompted for an install target, choose `.claude/skills`.

## Contents

- `.claude-plugin/marketplace.json` exposes this repository as a marketplace.
- `plugins/fastapicloud/.claude-plugin/plugin.json` is the plugin manifest.
- `plugins/fastapicloud/skills/` contains the FastAPI Cloud skills for app
  creation, deployment, integrations, logs, and environment variables.

## Install

```bash
/plugin marketplace add fastapicloud/skills
/plugin install fastapicloud@fastapicloud-skills
```

The plugin's skills are namespaced by the plugin name, e.g.
`/fastapicloud:fastapicloud-deploy`, `/fastapicloud:fastapi-new`,
`/fastapicloud:fastapicloud-integrations`, `/fastapicloud:fastapicloud-logs`,
and `/fastapicloud:fastapicloud-env`. Claude also invokes them automatically
based on task context.

Plugin versions are pinned and updated together with the release notes.

## Release preparation

`src/plugins/version.json`, the directly installable plugin manifests, and
`release-notes.md` are updated together by `scripts/prepare_release.py`.

```bash
uv run scripts/prepare_release.py --help
```

## Development

```bash
uvx ruff check .
uv run --no-project --with "pytest>=8,<10" --with "typer>=0.26.1" \
  python -m pytest --strict-config --strict-markers
claude plugin validate ./plugins/fastapicloud
```

The plugin is published under the MIT license.
