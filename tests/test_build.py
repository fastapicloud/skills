import json
import zipfile
from pathlib import Path

import pytest

import scripts.package_release as package_release_module
from scripts.build import ROOT, SKILL_NAMES, BuildError, build, current_version
from scripts.package_release import package_release
from scripts.validate import (
    DIRECT_MANIFESTS,
    EXPECTED_SKILL_PATHS,
    ValidationError,
    skill_frontmatter,
    validate_distribution,
    validate_source,
)


def test_builds_valid_codex_distribution(tmp_path: Path) -> None:
    output = tmp_path / "codex"
    build("codex", output)
    validate_distribution("codex", output, current_version())


def test_codex_uses_identical_top_level_skills(tmp_path: Path) -> None:
    output = tmp_path / "codex"
    build("codex", output)

    for skill_name in SKILL_NAMES:
        source = ROOT / skill_name
        built = output / "skills" / skill_name
        source_files = {
            path.relative_to(source): path.read_bytes()
            for path in source.rglob("*")
            if path.is_file()
        }
        built_files = {
            path.relative_to(built): path.read_bytes()
            for path in built.rglob("*")
            if path.is_file()
        }
        assert built_files == source_files


def test_direct_manifests_use_top_level_skill_paths() -> None:
    version = current_version()
    for relative_path in DIRECT_MANIFESTS:
        manifest = json.loads((ROOT / relative_path).read_text())
        assert manifest["version"] == version
        assert manifest["skills"] == EXPECTED_SKILL_PATHS

    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    assert marketplace["plugins"][0]["source"] == "./"


def test_source_layout_is_valid() -> None:
    validate_source()


def test_skill_frontmatter_requires_closing_delimiter(tmp_path: Path) -> None:
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("---\nname: example\ndescription: Example skill\n")

    with pytest.raises(ValidationError, match="Unterminated YAML frontmatter"):
        skill_frontmatter(skill_file)


def test_distribution_rejects_invalid_openai_metadata(tmp_path: Path) -> None:
    output = tmp_path / "codex"
    build("codex", output)
    metadata = output / "skills" / "fastapi-new" / "agents" / "openai.yaml"
    metadata.write_text("interface: [\n")

    with pytest.raises(ValidationError, match="Invalid YAML"):
        validate_distribution("codex", output, current_version())


def test_distribution_rejects_too_many_default_prompts(tmp_path: Path) -> None:
    output = tmp_path / "codex"
    build("codex", output)
    manifest_path = output / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["interface"]["defaultPrompt"].append("Configure another capability.")
    manifest_path.write_text(json.dumps(manifest))

    with pytest.raises(
        ValidationError,
        match="interface.defaultPrompt must contain at most 3 prompts",
    ):
        validate_distribution("codex", output, current_version())


def test_release_rejects_invalid_openai_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_build = package_release_module.build

    def build_with_invalid_metadata(target: str, output: Path, root: Path) -> None:
        original_build(target, output, root)
        metadata = output / "skills" / "fastapi-new" / "agents" / "openai.yaml"
        metadata.write_text("interface: [\n")

    monkeypatch.setattr(package_release_module, "build", build_with_invalid_metadata)
    output = tmp_path / "release"

    with pytest.raises(ValidationError, match="Invalid YAML"):
        package_release_module.package_release(output)

    assert not any(output.iterdir())


def test_build_refuses_non_empty_output(tmp_path: Path) -> None:
    output = tmp_path / "output"
    output.mkdir()
    (output / "keep-me").write_text("user data")

    with pytest.raises(BuildError, match="must be empty"):
        build("codex", output)

    assert (output / "keep-me").read_text() == "user data"


def test_release_archives_are_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    package_release(first)
    package_release(second)

    first_files = {path.name: path.read_bytes() for path in first.iterdir()}
    second_files = {path.name: path.read_bytes() for path in second.iterdir()}
    assert first_files == second_files
    assert set(first_files) == {
        f"fastapicloud-openai-{current_version()}.zip",
        "SHA256SUMS",
    }


def test_openai_archive_has_upload_root_layout(tmp_path: Path) -> None:
    output = tmp_path / "release"
    package_release(output)
    archive = next(output.glob("fastapicloud-openai-*.zip"))

    with zipfile.ZipFile(archive) as zip_file:
        names = set(zip_file.namelist())

    assert ".codex-plugin/plugin.json" in names
    assert "assets/logo.png" in names
    assert "skills/fastapi-new/SKILL.md" in names
    assert "skills/fastapi-new/agents/openai.yaml" in names
    assert not any(name.startswith("plugins/fastapicloud/") for name in names)
