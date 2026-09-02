# FastAPI Cloud (Codex plugin)

Generated Codex plugin for working with FastAPI Cloud from local FastAPI
projects: create apps, deploy, connect third-party resources, inspect logs, and
manage environment variables.

This directory is the direct plugin archive layout uploaded to OpenAI. Its
source of truth is
[`fastapicloud/skills`](https://github.com/fastapicloud/skills).

## Contents

- `.codex-plugin/plugin.json` contains the plugin manifest.
- `skills/` contains the FastAPI Cloud skills and their Codex metadata.
- `assets/` contains the plugin logo.

## Validate

```bash
uv run --with pyyaml python ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

The plugin is published under the MIT license.
