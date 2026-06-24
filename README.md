# FastAPI Cloud Plugin

Plugin for working with FastAPI Cloud from local FastAPI projects, packaged for
both **Codex** and **Claude Code**. Both share the same skills under
`plugins/fastapi-cloud/skills/` — only the manifest and marketplace files differ
per ecosystem.

## Contents

Shared:

- `plugins/fastapi-cloud/skills/` contains the FastAPI Cloud skills for app
  creation, deployment, logs, and environment variables. These `SKILL.md` files
  are used by both Codex and Claude Code.

Codex:

- `plugins/fastapi-cloud/.codex-plugin/plugin.json` — Codex plugin manifest.
- `.agents/plugins/marketplace.json` — Codex marketplace entry.
- `plugins/fastapi-cloud/skills/*/agents/openai.yaml` — Codex-only per-skill
  interface metadata (ignored by Claude Code).

Claude Code:

- `plugins/fastapi-cloud/.claude-plugin/plugin.json` — Claude Code plugin manifest.
- `.claude-plugin/marketplace.json` — Claude Code marketplace entry.

## Install in Claude Code

Add this repository as a marketplace, then install the plugin:

```bash
/plugin marketplace add fastapicloud/skills
/plugin install fastapi-cloud@fastapicloud-skills
```

To develop locally without going through GitHub, add the marketplace from a path:

```bash
/plugin marketplace add /Users/you/path/to/skills
```

The plugin's skills are namespaced by the plugin name, e.g.
`/fastapi-cloud:fastapi-cloud-deploy`, `/fastapi-cloud:fastapi-new`,
`/fastapi-cloud:fastapi-cloud-logs`, `/fastapi-cloud:fastapi-cloud-env`. Claude
also invokes them automatically based on task context.

> `.claude-plugin/plugin.json` intentionally omits `version`, so each git commit
> is treated as a new version and users receive updates on every push. To switch
> to pinned releases, add a `version` field and bump it on each release.

## Development

Validate the Claude Code manifest:

```bash
claude plugin validate ./plugins/fastapi-cloud
```

Validate the Codex plugin manifest before publishing or reinstalling locally:

```bash
uv run --with pyyaml python ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/fastapi-cloud
```

Validate a skill after editing its `SKILL.md`:

```bash
uv run --with pyyaml python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/fastapi-cloud/skills/fastapi-cloud-deploy
```

The plugin is published under the MIT license.
