"""Build provider-specific plugin distributions from the canonical skills."""

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "src" / "plugins"
SKILL_NAMES = (
    "fastapi-new",
    "fastapicloud-deploy",
    "fastapicloud-env",
    "fastapicloud-integrations",
    "fastapicloud-logs",
)
TARGETS = ("codex",)


class BuildError(RuntimeError):
    """Raised when a distribution cannot be built safely."""


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(data, indent=2, ensure_ascii=False)}\n")


def current_version(root: Path = ROOT) -> str:
    version = read_json(root / "src" / "plugins" / "version.json").get("version")
    if not isinstance(version, str):
        raise BuildError("src/plugins/version.json must contain a string version")
    return version


def copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, dirs_exist_ok=True)


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def prepare_output(output: Path) -> None:
    if output.exists() and any(output.iterdir()):
        raise BuildError(f"Output directory must be empty: {output}")
    output.mkdir(parents=True, exist_ok=True)


def copy_versioned_json(source: Path, destination: Path, version: str) -> None:
    data = read_json(source)
    data["version"] = version
    write_json(destination, data)


def build_codex(output: Path, version: str, root: Path = ROOT) -> None:
    template = root / "src" / "plugins" / "codex"
    copy_file(template / "README.md", output / "README.md")
    copy_file(root / "LICENSE", output / "LICENSE")
    copy_versioned_json(
        template / "plugin.json", output / ".codex-plugin" / "plugin.json", version
    )
    copy_file(template / "assets" / "logo.png", output / "assets" / "logo.png")
    for skill_name in SKILL_NAMES:
        copy_tree(root / skill_name, output / "skills" / skill_name)


BUILDERS = {"codex": build_codex}


def build(target: str, output: Path, root: Path = ROOT) -> None:
    if target not in BUILDERS:
        raise BuildError(f"Unknown target {target!r}; choose from {', '.join(TARGETS)}")
    prepare_output(output)
    BUILDERS[target](output, current_version(root), root)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=TARGETS)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(args.target, args.output)


if __name__ == "__main__":
    main()
