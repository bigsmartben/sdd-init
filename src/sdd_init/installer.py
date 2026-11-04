"""Verified directory replacement with rollback and local modification protection."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import uuid


def snapshot(folder: Path) -> dict[str, str]:
    result = {}
    for path in folder.rglob("*"):
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            raise ValueError(f"Linked installation path is not supported: {path}")
        if path.is_file() and path != folder / "build-manifest.json":
            result[path.relative_to(folder).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def verified(folder: Path) -> dict[str, str]:
    try:
        manifest = json.loads((folder / "build-manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError(f"Missing or invalid managed manifest; preserve existing files: {folder}") from error
    actual = snapshot(folder)
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1 or manifest.get("files") != actual:
        raise ValueError(f"Modified or untracked files; preserve existing files: {folder}")
    required = {"SKILL.md", "scripts/govern.py", "assets/repo-payload.zip"}
    if not required <= actual.keys():
        raise ValueError(f"Incomplete skill: {folder}")
    return actual


def install(resources: Path, skills_dir: Path) -> str:
    expected = verified(resources)
    # New releases require the recovery implementation. Older managed targets
    # remain verifiable so they can upgrade without a manual reinstall.
    if "scripts/project_install.py" not in expected:
        raise ValueError(f"Incomplete distribution: missing scripts/project_install.py: {resources}")
    skills_dir = skills_dir.expanduser().absolute()
    for path in (skills_dir, *skills_dir.parents):
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            raise ValueError(f"Linked installation path is not supported: {path}")
    skills_dir.mkdir(parents=True, exist_ok=True)
    target = skills_dir / "sdd-init"
    # Exclusive lock prevents concurrent installers from overwriting one another.
    lock = skills_dir / ".sdd-init-install.lock"
    handle = lock.open("x")
    try:
        if target.is_symlink() or (hasattr(target, "is_junction") and target.is_junction()):
            raise ValueError(f"Linked installation path is not supported: {target}")
        exists = target.exists()
        if exists and verified(target) == expected:
            return "Already current"
        with tempfile.TemporaryDirectory(prefix=".sdd-init-", dir=skills_dir) as temporary:
            staged = Path(temporary) / "skill"
            shutil.copytree(resources, staged)
            verified(staged)
            backup = skills_dir / (".sdd-init-backup-" + uuid.uuid4().hex)
            if exists:
                target.rename(backup)
            try:
                staged.rename(target)
            except OSError:
                if exists:
                    backup.rename(target)
                raise
            if exists:
                shutil.rmtree(backup)
        return "Updated" if exists else "Installed"
    finally:
        handle.close()
        lock.unlink()
