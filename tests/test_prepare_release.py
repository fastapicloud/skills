from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from scripts.prepare_release import (
    BumpType,
    app,
    bump_version,
    get_current_version,
    get_release_notes_body,
    parse_manifest_files,
    update_release_notes,
    update_version_file,
)

runner = CliRunner()


def version_content(version: str) -> str:
    return f'{{\n  "version": "{version}"\n}}\n'


@pytest.mark.parametrize(
    ("current_version", "bump", "new_version"),
    [
        ("0.18.0", BumpType.major, "1.0.0"),
        ("0.18.0", BumpType.minor, "0.19.0"),
        ("0.18.0", BumpType.patch, "0.18.1"),
    ],
)
def test_bump_version(current_version: str, bump: BumpType, new_version: str) -> None:
    assert bump_version(current_version, bump) == new_version


def test_update_version_file() -> None:
    content = version_content("0.18.0")

    new_content = update_version_file(content, "0.18.1", Path("version.json"))

    assert new_content == version_content("0.18.1")


def test_update_version_file_requires_newer_version() -> None:
    content = version_content("0.18.0")

    with pytest.raises(RuntimeError, match="must be greater"):
        update_version_file(content, "0.18.0", Path("version.json"))


def test_parse_manifest_files() -> None:
    assert parse_manifest_files(
        ".claude-plugin/plugin.json,.cursor-plugin/plugin.json,.grok-plugin/plugin.json"
    ) == [
        Path(".claude-plugin/plugin.json"),
        Path(".cursor-plugin/plugin.json"),
        Path(".grok-plugin/plugin.json"),
    ]


def test_manifest_files_must_be_unique() -> None:
    with pytest.raises(RuntimeError, match="must be unique"):
        parse_manifest_files("plugin.json,plugin.json")


def test_update_release_notes() -> None:
    content = """# Release Notes

## Latest Changes

### Fixes

* Fix something.

## 0.18.0 (2026-05-22)

### Fixes

* Previous fix.
"""

    new_content = update_release_notes(
        content, "0.18.1", date(2026, 5, 30), Path("release-notes.md")
    )

    assert (
        new_content
        == """# Release Notes

## Latest Changes

## 0.18.1 (2026-05-30)

### Fixes

* Fix something.

## 0.18.0 (2026-05-22)

### Fixes

* Previous fix.
"""
    )


def test_update_release_notes_rejects_existing_version() -> None:
    content = """# Release Notes

## Latest Changes

## 0.18.1 (2026-05-30)
"""

    with pytest.raises(RuntimeError, match="already contain"):
        update_release_notes(
            content, "0.18.1", date(2026, 5, 30), Path("release-notes.md")
        )


def test_get_release_notes_body_with_dated_heading() -> None:
    content = """# Release Notes

## Latest Changes

## 0.18.1 (2026-05-30)

### Fixes

* Fix something.

## 0.18.0 (2026-05-22)

### Fixes

* Previous fix.
"""

    body = get_release_notes_body(content, "0.18.1", Path("release-notes.md"))

    assert (
        body
        == """### Fixes

* Fix something.
"""
    )


def test_get_release_notes_body_with_plain_heading() -> None:
    content = """# Release Notes

## Latest Changes

## 0.18.1

### Fixes

* Fix something.
"""

    body = get_release_notes_body(content, "0.18.1", Path("release-notes.md"))

    assert body == "### Fixes\n\n* Fix something.\n"


def test_get_release_notes_body_allows_non_version_h2_content() -> None:
    content = """# Release Notes

## Latest Changes

## 0.18.1

## Highlights

* Fix something.

## 0.18.0

* Previous fix.
"""

    body = get_release_notes_body(content, "0.18.1", Path("release-notes.md"))

    assert body == "## Highlights\n\n* Fix something.\n"


def test_get_release_notes_body_requires_version_section() -> None:
    content = "# Release Notes\n\n## Latest Changes\n"

    with pytest.raises(RuntimeError, match="Could not find"):
        get_release_notes_body(content, "0.18.1", Path("release-notes.md"))


def test_get_release_notes_body_requires_non_empty_section() -> None:
    content = """# Release Notes

## Latest Changes

## 0.18.1

## 0.18.0

* Previous fix.
"""

    with pytest.raises(RuntimeError, match="is empty"):
        get_release_notes_body(content, "0.18.1", Path("release-notes.md"))


def test_cli_updates_configured_files(tmp_path: Path) -> None:
    version_file = tmp_path / "version.json"
    claude_manifest = tmp_path / "claude.json"
    cursor_manifest = tmp_path / "cursor.json"
    grok_manifest = tmp_path / "grok.json"
    release_notes_file = tmp_path / "release-notes.md"
    for path in (version_file, claude_manifest, cursor_manifest, grok_manifest):
        path.write_text(version_content("0.18.0"))
    release_notes_file.write_text(
        """# Release Notes

## Latest Changes

### Fixes

* Fix something.
"""
    )

    result = runner.invoke(
        app,
        [
            "prepare",
            "patch",
            "--version-file",
            str(version_file),
            "--plugin-manifest-files",
            f"{claude_manifest},{cursor_manifest},{grok_manifest}",
            "--release-notes-file",
            str(release_notes_file),
            "--date",
            "2026-05-30",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Prepared release 0.18.1 (2026-05-30)" in result.output
    for path in (version_file, claude_manifest, cursor_manifest, grok_manifest):
        assert get_current_version(path.read_text(), path) == "0.18.1"
    assert "## 0.18.1 (2026-05-30)" in release_notes_file.read_text()


def test_cli_rejects_mismatched_manifest_versions(tmp_path: Path) -> None:
    version_file = tmp_path / "version.json"
    manifest_file = tmp_path / "plugin.json"
    release_notes_file = tmp_path / "release-notes.md"
    version_file.write_text(version_content("0.18.0"))
    manifest_file.write_text(version_content("0.17.0"))
    release_notes_file.write_text(
        "# Release Notes\n\n## Latest Changes\n\n* Fix something.\n"
    )

    result = runner.invoke(
        app,
        [
            "prepare",
            "patch",
            "--version-file",
            str(version_file),
            "--plugin-manifest-files",
            str(manifest_file),
            "--release-notes-file",
            str(release_notes_file),
            "--date",
            "2026-05-30",
        ],
    )

    assert result.exit_code == 1
    assert isinstance(result.exception, RuntimeError)
    assert "Version mismatch" in str(result.exception)
    assert version_file.read_text() == version_content("0.18.0")
    assert manifest_file.read_text() == version_content("0.17.0")


def test_cli_accepts_env_vars(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    version_file = tmp_path / "version.json"
    claude_manifest = tmp_path / "claude.json"
    cursor_manifest = tmp_path / "cursor.json"
    grok_manifest = tmp_path / "grok.json"
    release_notes_file = tmp_path / "release-notes.md"
    for path in (version_file, claude_manifest, cursor_manifest, grok_manifest):
        path.write_text(version_content("0.18.0"))
    release_notes_file.write_text(
        "# Release Notes\n\n## Latest Changes\n\n* Fix something.\n"
    )
    monkeypatch.setenv("PREPARE_RELEASE_BUMP", "minor")
    monkeypatch.setenv("PREPARE_RELEASE_VERSION_FILE", str(version_file))
    monkeypatch.setenv(
        "PREPARE_RELEASE_PLUGIN_MANIFEST_FILES",
        f"{claude_manifest},{cursor_manifest},{grok_manifest}",
    )
    monkeypatch.setenv(
        "PREPARE_RELEASE_RELEASE_NOTES_FILE", str(release_notes_file)
    )
    monkeypatch.setenv("PREPARE_RELEASE_DATE", "2026-05-30")

    result = runner.invoke(app, ["prepare"])

    assert result.exit_code == 0, result.output
    assert "Prepared release 0.19.0 (2026-05-30)" in result.output
    for path in (version_file, claude_manifest, cursor_manifest, grok_manifest):
        assert get_current_version(path.read_text(), path) == "0.19.0"
    assert "## 0.19.0 (2026-05-30)" in release_notes_file.read_text()


def test_cli_prints_current_version(tmp_path: Path) -> None:
    version_file = tmp_path / "version.json"
    version_file.write_text(version_content("0.18.0"))

    result = runner.invoke(
        app,
        [
            "current-version",
            "--version-file",
            str(version_file),
        ],
    )

    assert result.exit_code == 0, result.output
    assert result.output == "0.18.0\n"


def test_cli_prints_release_notes(tmp_path: Path) -> None:
    version_file = tmp_path / "version.json"
    version_file.write_text(version_content("0.18.1"))
    release_notes_file = tmp_path / "release-notes.md"
    release_notes_file.write_text(
        """# Release Notes

## Latest Changes

## 0.18.1 (2026-05-30)

### Fixes

* Fix something.
"""
    )

    result = runner.invoke(
        app,
        [
            "release-notes",
            "--version-file",
            str(version_file),
            "--release-notes-file",
            str(release_notes_file),
        ],
    )

    assert result.exit_code == 0, result.output
    assert result.output == "### Fixes\n\n* Fix something.\n"
