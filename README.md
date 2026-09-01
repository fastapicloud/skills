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

Release archives use the direct plugin root expected by OpenAI. Build an upload
archive with:

```bash
python scripts/package_release.py dist/releases
```

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

## Release preparation

`src/plugins/version.json`, the directly installable plugin manifests, and
`release-notes.md` are updated together by `scripts/prepare_release.py`.

```bash
uv run scripts/prepare_release.py --help
```

The skills and plugin metadata are published under the MIT license.
