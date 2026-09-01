# FastAPI Cloud agent skills

One repository for FastAPI Cloud skills across Claude Code, Codex, Grok Build,
and Amp. The same top-level skill directories are the source of truth for every
client; provider manifests are small adapters and are never maintained in
separate generated repositories.

## Repository layout

```text
fastapi-new/SKILL.md
fastapicloud-deploy/SKILL.md
fastapicloud-env/SKILL.md
fastapicloud-integrations/SKILL.md
fastapicloud-logs/SKILL.md
.claude-plugin/                 # Direct Claude Code plugin and marketplace
.grok-plugin/                   # Direct Grok Build plugin
src/plugins/codex/              # Codex archive metadata
```

Each skill is an immediate child of the repository root so Amp can install the
repository without a subpath. Claude and Grok use explicit paths in their
manifests to load those same directories. The release builder copies them into
Codex's required `skills/` directory without changing their contents.

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
uv run --no-project --with "pytest>=8,<10" --with "typer>=0.26.1" \
  python -m pytest --strict-config --strict-markers
python scripts/validate.py --source

python scripts/build.py codex dist/codex
python scripts/validate.py codex dist/codex
python scripts/package_release.py dist/releases
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

The skills and plugin metadata are published under the MIT license.
