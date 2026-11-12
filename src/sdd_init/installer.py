"""Verified directory replacement with rollback and local modification protection."""
from collections.abc import Collection
import hashlib
from importlib.util import source_from_cache
import json
from pathlib import Path
import shutil
import tempfile
import uuid


def is_bytecode_for_managed_source(path: Path, installed_files: Collection[str]) -> bool:
    if not installed_files or path.parent.name != "__pycache__" or path.suffix != ".pyc":
        return False
    try:
        return Path(source_from_cache(path)).as_posix() in installed_files
    except (NotImplementedError, ValueError):
        return False


def snapshot(folder: Path, *, installed_files: Collection[str] = ()) -> dict[str, str]:
    result = {}
    for path in folder.rglob("*"):
        if is_linked(path):
            raise ValueError(f"Linked installation path is not supported: {path}")
        if path.is_file() and path != folder / "build-manifest.json":
            relative = path.relative_to(folder)
            name = relative.as_posix()
            if name not in installed_files and is_bytecode_for_managed_source(relative, installed_files):
                continue
            result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def shared_directory(skills_dir: Path) -> Path:
    return skills_dir.with_name(f"{skills_dir.name}-sdd-init-shared")


def verified(folder: Path, *, shared: Path | None = None) -> dict[str, str]:
    try:
        manifest = json.loads((folder / "build-manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError(f"Missing or invalid managed manifest; preserve existing files: {folder}") from error
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(files, dict) or manifest.get("schema_version") != 1:
        raise ValueError(f"Missing or invalid managed manifest; preserve existing files: {folder}")
    actual = snapshot(folder, installed_files=files if shared is not None else ())
    has_shared = any(name.startswith("shared/") for name in files)
    if shared is not None and has_shared:
        if not shared.is_dir() or is_linked(shared) or (folder / "shared").exists():
            raise ValueError(f"Missing or invalid shared installation: {shared}")
        shared_files = {name.removeprefix("shared/") for name in files if name.startswith("shared/")}
        actual.update({f"shared/{name}": digest for name, digest in
                       snapshot(shared, installed_files=shared_files).items()})
    elif shared is not None and (shared.exists() or is_linked(shared)):
        raise ValueError(f"Unexpected shared installation; preserve existing files: {shared}")
    if files != actual:
        raise ValueError(f"Modified or untracked files; preserve existing files: {folder}")
    required = {"SKILL.md", "scripts/govern.py"}
    required.add("shared/sdd/references/delegation.md" if has_shared else "assets/repo-payload.zip")
    if not required <= actual.keys():
        raise ValueError(f"Incomplete skill: {folder}")
    return actual


def is_linked(path: Path) -> bool:
    try:
        return path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400)
    except FileNotFoundError:
        return False


def install(resources: Path, skills_dir: Path) -> str:
    expected = verified(resources)
    # New releases require the recovery implementation. Older managed targets
    # remain verifiable so they can upgrade without a manual reinstall.
    for name in ("scripts/project_install.py", "shared/sdd/references/delegation.md"):
        if name not in expected:
            raise ValueError(f"Incomplete distribution: missing {name}: {resources}")
    skills_dir = skills_dir.expanduser().absolute()
    for path in (skills_dir, *skills_dir.parents):
        if is_linked(path):
            raise ValueError(f"Linked installation path is not supported: {path}")
    skills_dir.mkdir(parents=True, exist_ok=True)
    target = skills_dir / "sdd-init"
    shared = shared_directory(skills_dir)
    # Exclusive lock prevents concurrent installers from overwriting one another.
    lock = skills_dir / ".sdd-init-install.lock"
    handle = lock.open("x")
    try:
        for path in (target, shared):
            if is_linked(path):
                raise ValueError(f"Linked installation path is not supported: {path}")
        exists = target.exists()
        if exists and verified(target, shared=shared) == expected:
            return "Already current"
        if not exists and shared.exists():
            raise ValueError(f"Unexpected shared installation; preserve existing files: {shared}")
        with tempfile.TemporaryDirectory(prefix=".sdd-init-", dir=skills_dir.parent) as temporary:
            staged = Path(temporary) / "skill"
            shutil.copytree(resources, staged)
            verified(staged)
            backup = skills_dir.parent / (".sdd-init-backup-" + uuid.uuid4().hex)
            backup.mkdir()
            saved, published = [], []
            try:
                for path in (target, shared):
                    if path.exists():
                        saved_path = backup / path.name
                        path.rename(saved_path)
                        saved.append((path, saved_path))
                (staged / "shared").rename(shared)
                published.append(shared)
                staged.rename(target)
                published.append(target)
                verified(target, shared=shared)
            except (OSError, ValueError):
                for path in reversed(published):
                    shutil.rmtree(path)
                for path, saved_path in reversed(saved):
                    saved_path.rename(path)
                backup.rmdir()
                raise
            shutil.rmtree(backup)
        return "Updated" if exists else "Installed"
    finally:
        handle.close()
        lock.unlink()
