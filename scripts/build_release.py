"""Build an installable SDD skill without modifying installed environments."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def source_files(folder: Path) -> list[Path]:
    files = []
    for path in sorted(folder.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlink is not a distribution source: {path}")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            files.append(path)
    return files


def build(output: Path) -> Path:
    output = output.resolve()
    # Keep generated artifacts out of both canonical sources and provenance.
    for protected in (ROOT / "source", ROOT / "baselines"):
        protected = protected.resolve()
        if output == protected or protected in output.parents:
            raise ValueError(f"Output overlaps maintained input: {output}")
    if output.exists():
        raise FileExistsError(f"Output already exists; use a new path: {output}")
    initializer = ROOT / "source/initializer"
    project = ROOT / "source/project"
    project_files = source_files(project)
    initializer_files = source_files(initializer)
    if not project_files or not initializer_files:
        raise ValueError("Missing distribution sources")
    output.mkdir(parents=True)
    for path in initializer_files:
        dest = output / path.relative_to(initializer)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
    shared = project / ".agents/sdd"
    for folder in ("assets", "references"):
        for path in source_files(shared / folder):
            dest = output / folder / path.relative_to(shared / folder)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)
    archive_path = output / "assets/repo-payload.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in project_files:
            info = zipfile.ZipInfo(path.relative_to(project).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    manifest = {
        "schema_version": 1,
        "files": {
            path.relative_to(output).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in source_files(output)
        },
    }
    (output / "build-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".build/sdd-init")
    args = parser.parse_args()
    print(build(args.output))


if __name__ == "__main__":
    main()
