# /// script
# requires-python = ">=3.14"
# dependencies = ["pyyaml>=6,<7"]
# ///

"""Validate canonical sources and built plugin distributions."""

import argparse
import json
import re
import tempfile
from pathlib import Path

import yaml

try:
    from .build import ROOT, SKILL_NAMES, TARGETS, build, current_version
except ImportError:  # Support `python scripts/validate.py`.
    from build import ROOT, SKILL_NAMES, TARGETS, build, current_version

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
EXPECTED_SKILLS = set(SKILL_NAMES)
DIRECT_MANIFESTS = (
    Path(".claude-plugin/plugin.json"),
    Path(".cursor-plugin/plugin.json"),
    Path(".grok-plugin/plugin.json"),
)
EXPECTED_SKILL_PATHS = [f"./{name}/" for name in SKILL_NAMES]
OPENAI_METADATA_FIELDS = {"interface", "policy", "dependencies"}
OPENAI_INTERFACE_FIELDS = {
    "display_name",
    "short_description",
    "icon_small",
    "icon_large",
    "brand_color",
    "default_prompt",
}


class ValidationError(RuntimeError):
    """Raised when a source or distribution violates the shared contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: Path) -> dict[str, object]:
    require(path.is_file(), f"Missing JSON file: {path}")
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise ValidationError(f"Invalid JSON in {path}: {error}") from error
    require(isinstance(payload, dict), f"Expected a JSON object in {path}")
    return payload


def parse_yaml_object(content: str, path: Path) -> dict[str, object]:
    try:
        payload = yaml.safe_load(content)
    except yaml.YAMLError as error:
        raise ValidationError(f"Invalid YAML in {path}: {error}") from error
    require(isinstance(payload, dict), f"Expected a YAML object in {path}")
    require(
        all(isinstance(key, str) for key in payload),
        f"Expected string keys in {path}",
    )
    return payload


def load_yaml(path: Path) -> dict[str, object]:
    require(path.is_file(), f"Missing YAML file: {path}")
    return parse_yaml_object(path.read_text(), path)


def require_known_fields(
    payload: dict[str, object], allowed_fields: set[str], path: Path
) -> None:
    unexpected_fields = set(payload) - allowed_fields
    require(
        not unexpected_fields,
        f"Unexpected fields in {path}: {sorted(unexpected_fields)}",
    )


def require_non_empty_string(
    payload: dict[str, object], field: str, path: Path
) -> str:
    value = payload.get(field)
    require(
        isinstance(value, str) and bool(value.strip()),
        f"Expected a non-empty {field!r} in {path}",
    )
    return value


def skill_frontmatter(path: Path) -> dict[str, object]:
    content = path.read_text()
    require(content.startswith("---\n"), f"Missing YAML frontmatter in {path}")
    frontmatter = content[4:]
    closing_delimiter = re.search(r"^---[ \t]*$", frontmatter, re.MULTILINE)
    require(closing_delimiter is not None, f"Unterminated YAML frontmatter in {path}")
    return parse_yaml_object(frontmatter[: closing_delimiter.start()], path)


def validate_openai_metadata(skill: Path) -> None:
    metadata_path = skill / "agents" / "openai.yaml"
    metadata = load_yaml(metadata_path)
    require_known_fields(metadata, OPENAI_METADATA_FIELDS, metadata_path)

    interface = metadata.get("interface")
    require(isinstance(interface, dict), f"Expected an interface object in {metadata_path}")
    require(
        all(isinstance(key, str) for key in interface),
        f"Expected string interface keys in {metadata_path}",
    )
    require_known_fields(interface, OPENAI_INTERFACE_FIELDS, metadata_path)
    require_non_empty_string(interface, "display_name", metadata_path)
    require_non_empty_string(interface, "short_description", metadata_path)

    default_prompt = interface.get("default_prompt")
    require(
        default_prompt is None
        or (isinstance(default_prompt, str) and bool(default_prompt.strip())),
        f"Expected a non-empty 'default_prompt' in {metadata_path}",
    )

    brand_color = interface.get("brand_color")
    require(
        brand_color is None
        or (isinstance(brand_color, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", brand_color)),
        f"Expected 'brand_color' to use #RRGGBB in {metadata_path}",
    )

    policy = metadata.get("policy")
    if policy is not None:
        require(isinstance(policy, dict), f"Expected a policy object in {metadata_path}")
        require(
            set(policy) <= {"allow_implicit_invocation"},
            f"Unexpected policy fields in {metadata_path}",
        )
        allow_implicit_invocation = policy.get("allow_implicit_invocation")
        require(
            allow_implicit_invocation is None
            or isinstance(allow_implicit_invocation, bool),
            f"Expected 'allow_implicit_invocation' to be a boolean in {metadata_path}",
        )

    dependencies = metadata.get("dependencies")
    if dependencies is not None:
        require(
            isinstance(dependencies, dict),
            f"Expected a dependencies object in {metadata_path}",
        )
        require(
            set(dependencies) <= {"tools"},
            f"Unexpected dependency fields in {metadata_path}",
        )


def validate_skill(skill: Path, *, codex_metadata: bool) -> None:
    skill_file = skill / "SKILL.md"
    require(skill_file.is_file(), f"Missing skill instructions: {skill_file}")
    metadata = skill_frontmatter(skill_file)
    require_non_empty_string(metadata, "name", skill_file)
    require(metadata["name"] == skill.name, f"Skill name mismatch in {skill_file}")
    require_non_empty_string(metadata, "description", skill_file)
    if codex_metadata:
        validate_openai_metadata(skill)


def validate_skills(skills: Path, *, codex_metadata: bool = False) -> None:
    require(skills.is_dir(), f"Missing skills directory: {skills}")
    skill_names = {path.name for path in skills.iterdir() if path.is_dir()}
    require(
        skill_names == EXPECTED_SKILLS,
        f"Unexpected skills in {skills}: {sorted(skill_names)}",
    )
    for name in sorted(skill_names):
        validate_skill(skills / name, codex_metadata=codex_metadata)


def validate_top_level_skills(root: Path) -> None:
    for name in SKILL_NAMES:
        skill = root / name
        require(skill.parent == root, f"Amp skill is not top-level: {skill}")
        validate_skill(skill, codex_metadata=True)


def validate_direct_manifest(root: Path, relative_path: Path, version: str) -> None:
    manifest_path = root / relative_path
    manifest = load_json(manifest_path)
    require(manifest.get("name") == "fastapicloud", f"Wrong name in {manifest_path}")
    require(
        manifest.get("version") == version,
        f"Version mismatch in {manifest_path}",
    )
    require(
        manifest.get("repository") == "https://github.com/fastapicloud/skills",
        f"Wrong repository in {manifest_path}",
    )
    require(
        manifest.get("skills") == EXPECTED_SKILL_PATHS,
        f"Unexpected skill paths in {manifest_path}",
    )


def validate_distribution(target: str, distribution: Path, version: str) -> None:
    require(target in TARGETS, f"Unknown target: {target}")
    require(SEMVER.fullmatch(version) is not None, f"Invalid version: {version}")
    require((distribution / "README.md").is_file(), f"Missing README in {distribution}")
    require((distribution / "LICENSE").is_file(), f"Missing LICENSE in {distribution}")

    manifest_path = distribution / ".codex-plugin" / "plugin.json"
    manifest = load_json(manifest_path)
    require(manifest.get("name") == "fastapicloud", f"Wrong name in {manifest_path}")
    require(
        manifest.get("version") == version,
        f"Version mismatch in {manifest_path}: {manifest.get('version')!r} != {version!r}",
    )
    require((distribution / "assets" / "logo.png").is_file(), "Missing Codex logo")
    validate_skills(distribution / "skills", codex_metadata=True)


def validate_source(root: Path = ROOT) -> None:
    version = current_version(root)
    require(SEMVER.fullmatch(version) is not None, f"Invalid canonical version: {version}")
    validate_top_level_skills(root)
    for manifest in DIRECT_MANIFESTS:
        validate_direct_manifest(root, manifest, version)

    cursor_manifest_path = root / ".cursor-plugin" / "plugin.json"
    cursor_manifest = load_json(cursor_manifest_path)
    cursor_logo = cursor_manifest.get("logo")
    require(
        isinstance(cursor_logo, str) and (root / cursor_logo).is_file(),
        f"Missing Cursor logo referenced by {cursor_manifest_path}",
    )

    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    marketplace = load_json(marketplace_path)
    plugins = marketplace.get("plugins")
    require(isinstance(plugins, list) and len(plugins) == 1, "Unexpected Claude plugins")
    plugin = plugins[0]
    require(isinstance(plugin, dict), "Invalid Claude marketplace plugin entry")
    require(plugin.get("source") == "./", "Claude marketplace must use the repo root")

    require(
        not (root / "plugins" / "fastapicloud").exists(),
        "Legacy nested plugin source still exists",
    )

    with tempfile.TemporaryDirectory() as temporary_directory:
        output = Path(temporary_directory) / "codex"
        build("codex", output, root)
        validate_distribution("codex", output, version)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=TARGETS, nargs="?")
    parser.add_argument("distribution", type=Path, nargs="?")
    parser.add_argument("--source", action="store_true")
    args = parser.parse_args()

    if args.source:
        require(args.target is None and args.distribution is None, "Use --source by itself")
        validate_source()
        return
    require(args.target is not None, "A target or --source is required")
    require(args.distribution is not None, "A distribution path is required")
    validate_distribution(args.target, args.distribution, current_version())


if __name__ == "__main__":
    main()
