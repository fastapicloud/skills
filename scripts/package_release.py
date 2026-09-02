# /// script
# requires-python = ">=3.14"
# dependencies = ["pyyaml>=6,<7"]
# ///

"""Build the deterministic OpenAI plugin release archive."""

import argparse
import hashlib
import tempfile
import zipfile
from pathlib import Path

try:
    from .build import ROOT, build, current_version
    from .validate import validate_distribution
except ImportError:  # Support `python scripts/package_release.py`.
    from build import ROOT, build, current_version
    from validate import validate_distribution

ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def archive_tree(source: Path, destination: Path) -> None:
    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in sorted(item for item in source.rglob("*") if item.is_file()):
            relative = path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(relative, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_release(output: Path, root: Path = ROOT) -> list[Path]:
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"Output directory must be empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    version = current_version(root)

    with tempfile.TemporaryDirectory() as temporary_directory:
        distribution = Path(temporary_directory) / "codex"
        build("codex", distribution, root)
        validate_distribution("codex", distribution, version)

        archive = output / f"fastapicloud-openai-{version}.zip"
        archive_tree(distribution, archive)

    checksums = output / "SHA256SUMS"
    checksums.write_text(f"{sha256(archive)}  {archive.name}\n")
    return [archive, checksums]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    for artifact in package_release(args.output):
        print(artifact)


if __name__ == "__main__":
    main()
