# FastAPI Cloud agent skills

One repository for FastAPI Cloud skills across Cursor and Grok Bot, Claude
Code, Codex and ChatGPT, Grok Build, and Amp. The same top-level skill
directories are the source of truth for every client; provider manifests are
small adapters and are never maintained in separate generated repositories.

## Repository layout

```text
fastapi-new/SKILL.md
fastapicloud-deploy/SKILL.md
fastapicloud-domains/SKILL.md
fastapicloud-env/SKILL.md
fastapicloud-integrations/SKILL.md
fastapicloud-logs/SKILL.md
.claude-plugin/                 # Direct Claude Code plugin and marketplace
.cursor-plugin/                 # Cursor and Grok Bot marketplace plugin
.grok-plugin/                   # Direct Grok Build plugin
src/plugins/codex/              # Codex archive metadata
```

Each skill is an immediate child of the repository root so Amp can install the
repository without a subpath. Claude, Cursor, and Grok Build use explicit paths
in their manifests to load those same directories. The release builder copies
them into Codex's required `skills/` directory without changing their contents.

## Install

### Amp

```bash
amp skill add fastapicloud/skills
```

### Claude Code

```bash
/plugin marketplace add fastapicloud/skills
/plugin install fastapicloud@fastapicloud-skills
/reload-plugins
```

The skills are namespaced by the plugin name, for example
`/fastapicloud:fastapicloud-deploy`. Claude also invokes them automatically
when relevant.

### Cursor and Grok Bot

Install **FastAPI Cloud** from the
[Cursor Marketplace](https://cursor.com/marketplace). Cursor and Grok Bot use
the same marketplace plugin.

### Grok Build

```bash
grok plugin install fastapicloud/skills --trust
```

### Codex and ChatGPT

Releases attach `fastapicloud-openai-<version>.zip`, which has the direct plugin
root expected by OpenAI. Upload that archive to the OpenAI plugin platform.

## FastAPI framework skills

After creating a project, install the framework and dependency-specific skills
provided by the installed packages:

```bash
uvx library-skills        # Python projects
npx library-skills        # JavaScript and TypeScript projects
```

When prompted, choose the skill directory for the active coding agent.

## Build and validate

The tooling is Python-based and uses uv for isolated dependencies.

```bash
uvx ruff check .
uv run --no-project --with "pytest>=8,<10" --with "pyyaml>=6,<7" \
  --with "typer>=0.26.1" \
  python -m pytest --strict-config --strict-markers
uv run scripts/validate.py --source

python scripts/build.py codex dist/codex
uv run scripts/validate.py codex dist/codex
uv run scripts/package_release.py dist/releases
```

Build commands refuse to write into non-empty output directories. Release ZIPs
are deterministic and accompanied by `SHA256SUMS`.

## Releases

The release flow mirrors `fastapilabs/fastapi-cloud-cli`. The Latest Changes
GitHub App records merged pull request titles in `release-notes.md`; do not edit
`## Latest Changes` manually.

1. Run the **Prepare Release** workflow and choose patch, minor, or major.
2. Merge the generated release pull request.
3. Review and publish the draft GitHub release.
4. Publishing attaches the OpenAI ZIP and its checksum to the release.

### Publish marketplace updates

Publishing the GitHub release does not update external marketplaces. After the
release is public:

1. Confirm `fastapicloud-openai-<version>.zip` and `SHA256SUMS` are attached to
   the GitHub release.
2. For Cursor and Grok Bot, submit a new listing or update the existing listing
   at the [Cursor Marketplace publisher](https://cursor.com/marketplace/publish).
   Marketplace updates are reviewed before they become available.
3. For Codex and ChatGPT, create or update the plugin at the
   [OpenAI plugin platform](https://platform.openai.com/plugins) and upload the
   release ZIP.
4. To publish in Grok Build's official catalog, update the plugin's pinned
   commit in [xAI's plugin marketplace](https://github.com/xai-org/plugin-marketplace),
   regenerate and validate its index as directed by that repository, and open a
   pull request.
5. Smoke-test the Amp, Claude Code, and Grok Build install commands above from
   the released `main` branch.

The skills and plugin metadata are published under the MIT license.
