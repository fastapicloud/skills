# FastAPI Cloud Codex Plugin

Codex plugin for working with FastAPI Cloud from local FastAPI projects.

## Contents

- `plugins/fastapi-cloud/.codex-plugin/plugin.json` contains the plugin manifest and marketplace metadata.
- `plugins/fastapi-cloud/skills/` contains the FastAPI Cloud skills for app creation, deployment, logs, and environment variables.
- `.agents/plugins/marketplace.json` exposes the plugin from this repository as a local marketplace entry.

## Development

Validate the plugin manifest before publishing or reinstalling locally:

```bash
uv run --with pyyaml python ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/fastapi-cloud
```

Validate a skill after editing its `SKILL.md`:

```bash
uv run --with pyyaml python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/fastapi-cloud/skills/fastapi-cloud-deploy
```

The plugin is published under the MIT license.
