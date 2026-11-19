"""Build an installable SDD skill without modifying installed environments."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tomllib

ROOT = Path(__file__).resolve().parent.parent


def source_files(folder: Path) -> list[Path]:
    files = []
    for path in sorted(folder.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlink is not a distribution source: {path}")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            files.append(path)
    return files


def copilot_adapter(name: str, description: str) -> str:
    prompt = (
        "---\n"
        f"name: {json.dumps(name, ensure_ascii=False)}\n"
        f"description: {json.dumps(description, ensure_ascii=False)}\n"
        "---\n"
        f"Read and follow `.github/sdd-workflow/roles/shared/{name}.md` before acting. "
        "That file is the authoritative role contract. "
        "In this Copilot adapter, use `.github/sdd-workflow/` as the actual shared-resource "
        "root named by the contract and task, so this harness can access the shared files. "
        "If it is unavailable on this execution host, report the missing sdd-init connection "
        "and stop; do not substitute a different role contract.\n"
    )
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    adapter = f"{prompt}<!-- sdd-init managed role {name} sha256:{digest} -->\n"
    if len(adapter) > 30_000:
        raise ValueError(f"Copilot role exceeds the 30,000-character prompt limit: {name}")
    return adapter


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
    initializer_files = source_files(initializer)
    if not initializer_files:
        raise ValueError("Missing distribution sources")
    output.mkdir(parents=True)
    for path in initializer_files:
        dest = output / path.relative_to(initializer)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
    shutil.copyfile(ROOT / "src/sdd_init/release.py", output / "scripts/release.py")
    for source, destination in ((".agents/skills", "skills"), (".agents/sdd", "sdd")):
        directory = project / source
        files = source_files(directory)
        if not files:
            raise ValueError(f"Missing distribution source: {directory}")
        for path in files:
            dest = output / "shared" / destination / path.relative_to(directory)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)

    role_source = project / ".codex/agents"
    role_files = source_files(role_source)
    if not role_files:
        raise ValueError(f"Missing distribution source: {role_source}")
    roles = output / "shared/roles"
    for path in role_files:
        relative = path.relative_to(role_source)
        if path.suffix == ".toml":
            role = tomllib.loads(path.read_text(encoding="utf-8"))
            fields = {"name", "description", "developer_instructions"}
            if (set(role) != fields or role["name"] != path.stem
                    or not all(isinstance(value, str) and value.strip() for value in role.values())):
                raise ValueError(f"Invalid role source: {path}")
            name, description = role["name"], role["description"]
            shared_contract = roles / "shared" / f"{name}.md"
            shared_contract.parent.mkdir(parents=True, exist_ok=True)
            shared_contract.write_text(role["developer_instructions"].strip() + "\n", encoding="utf-8")

            codex_instructions = (
                f"Read and follow .agents/sdd-workflow/roles/shared/{name}.md before acting. "
                "That file is the authoritative role contract."
            )
            # Existing project configs still resolve this path after a user-level upgrade.
            legacy_instructions = (
                f"Read and follow .agents/sdd-workflow/roles/shared/{name}.md before acting. "
                "If that file is absent, read and follow "
                f".agents/skills/sdd-workflow/roles/shared/{name}.md instead and use "
                ".agents/skills/sdd-workflow/sdd/ as the shared resource root."
            )
            for directory, instructions in ((roles / "codex", codex_instructions),
                                            (output / "shared/agents", legacy_instructions)):
                directory.mkdir(parents=True, exist_ok=True)
                codex = {"name": name, "description": description, "developer_instructions": instructions}
                (directory / f"{name}.toml").write_text(
                    "\n".join(f"{key} = {json.dumps(value, ensure_ascii=False)}"
                              for key, value in codex.items()) + "\n",
                    encoding="utf-8",
                )

            copilot_path = roles / "copilot" / f"{name}.agent.md"
            copilot_path.parent.mkdir(parents=True, exist_ok=True)
            adapter = copilot_adapter(name, description)
            copilot_path.write_text(adapter, encoding="utf-8", newline="\n")
        else:
            destination = roles / "shared" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
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
