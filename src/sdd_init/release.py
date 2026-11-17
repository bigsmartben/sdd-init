"""Verify the same bundle format from the CLI and the installed project tool."""
from __future__ import annotations

from collections.abc import Collection
from contextlib import contextmanager
import hashlib
from importlib.util import source_from_cache
import json
import os
from pathlib import Path
import re
import stat
import tomllib

MANIFEST = "build-manifest.json"
USER_LOCK = ".sdd-init-install.lock"
LOCK_BYTES = b"sdd-init lock v1\n"
USER_ROLE = "review-prompt"
# Only used to identify and recover the former standalone user installation.
USER_ROLE_ASSET = f"assets/user-agents/{USER_ROLE}.toml"
WORKFLOW_REVIEW_ROLE = f"shared/agents/{USER_ROLE}.toml"


def shared_directory(skills_dir: Path) -> Path:
    return skills_dir.with_name(f"{skills_dir.name}-sdd-init-shared")


def recovery_directory(skills_dir: Path) -> Path:
    return skills_dir.with_name(f".{skills_dir.name}-sdd-init-install-recovery")


def linked(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


@contextmanager
def user_lock(directory: Path, *, shared_read: bool = False, name: str = USER_LOCK):
    path = directory / name
    if linked(path):
        raise ValueError(f"Linked installation lock: {path}")
    if not shared_read:
        try:
            with path.open("xb") as handle:
                handle.write(LOCK_BYTES)
                handle.flush()
                os.fsync(handle.fileno())
        except FileExistsError:
            pass
    if not path.exists() and shared_read:
        # Pre-lock installations have no stable metadata. The project installer
        # additionally rechecks the full release before and after changes.
        yield
        return
    with path.open("rb" if shared_read else "r+b") as handle:
        # The Windows writer's lock protects byte zero. Readers can verify
        # the lock format from the remaining bytes and recheck the release.
        if shared_read and os.name == "nt":
            handle.seek(1)
            if handle.read() != LOCK_BYTES[1:]:
                raise FileExistsError(f"Legacy or invalid installation lock; preserve and inspect: {path}")
            yield
            return
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                mode = fcntl.LOCK_SH if shared_read else fcntl.LOCK_EX
                fcntl.flock(handle.fileno(), mode | fcntl.LOCK_NB)
        except OSError as error:
            raise FileExistsError(f"Shared installation in progress: {path}") from error
        if handle.read() != LOCK_BYTES:
            raise FileExistsError(f"Legacy or invalid installation lock; preserve and inspect: {path}")
        yield


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def entry_exists(path: Path) -> bool:
    return path.exists() or linked(path)


def entry_inventory(path: Path, *, exclude_shared: bool = False) -> dict | None:
    """Record an entry without following links or junctions."""
    if not entry_exists(path):
        return None
    entries = {}
    pending = [(path, ".")]
    while pending:
        current, relative = pending.pop()
        info = current.lstat()
        mode = stat.S_IMODE(info.st_mode)
        if linked(current):
            entries[relative] = ["link", mode, os.readlink(current)]
        elif current.is_dir():
            entries[relative] = ["directory", mode]
            for child in current.iterdir():
                if exclude_shared and relative == "." and child.name == "shared":
                    continue
                name = child.name if relative == "." else f"{relative}/{child.name}"
                pending.append((child, name))
        elif current.is_file():
            entries[relative] = ["file", mode, digest(current.read_bytes())]
        else:
            raise ValueError(f"Unsupported installation entry: {current}")
    return entries


def inventory_digest(entries: dict | None) -> str | None:
    return None if entries is None else digest(json.dumps(entries, sort_keys=True, ensure_ascii=True).encode("utf-8"))


def entry_snapshot(path: Path, *, exclude_shared: bool = False) -> str | None:
    return inventory_digest(entry_inventory(path, exclude_shared=exclude_shared))


def content_id(files: dict[str, str]) -> str:
    return digest(json.dumps(files, sort_keys=True, separators=(",", ":")).encode())


def manifest_data(folder: Path) -> dict:
    path = folder / MANIFEST
    try:
        if linked(folder) or linked(path) or not path.is_file():
            raise ValueError(f"Missing or linked manifest: {path}")
        manifest = json.loads(path.read_text(encoding="utf-8"))
        files = manifest.get("files") if isinstance(manifest, dict) else None
        if (not isinstance(files, dict) or manifest.get("schema_version") != 1
                or not all(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)
                           for value in files.values())):
            raise ValueError("Invalid manifest format")
        return manifest
    except (OSError, ValueError) as error:
        raise ValueError(f"Missing or invalid managed manifest; preserve existing files: {path}") from error


def read_manifest(folder: Path) -> dict[str, str]:
    return manifest_data(folder)["files"]


def shared_files(files: dict[str, str]) -> dict[str, str]:
    return {name.removeprefix("shared/"): value for name, value in files.items() if name.startswith("shared/")}


def is_bytecode_for_managed_source(path: Path, installed_files: Collection[str]) -> bool:
    if not installed_files or path.parent.name != "__pycache__" or path.suffix != ".pyc":
        return False
    try:
        return Path(source_from_cache(path)).as_posix() in installed_files
    except (NotImplementedError, ValueError):
        return False


def snapshot(folder: Path, *, installed_files: Collection[str] = (), exclude_manifest: bool = True) -> dict[str, str]:
    if not folder.is_dir() or linked(folder):
        raise ValueError(f"Missing or linked installation directory: {folder}")
    def raise_walk_error(error):
        raise error

    # Iterating member by member catches linked directories even on hosts that
    # would follow a junction during a recursive glob.
    result = {}
    for directory, children, filenames in os.walk(folder, onerror=raise_walk_error):
        for name in children + filenames:
            path = Path(directory) / name
            if linked(path):
                raise ValueError(f"Linked installation path is not supported: {path}")
        for name in filenames:
            path = Path(directory) / name
            relative = path.relative_to(folder)
            key = relative.as_posix()
            if exclude_manifest and key == MANIFEST:
                continue
            if not path.is_file():
                raise ValueError(f"Not a regular file: {path}")
            if key not in installed_files and is_bytecode_for_managed_source(relative, installed_files):
                continue
            result[key] = digest(path.read_bytes())
    return result


def check_files(expected: dict[str, str], actual: dict[str, str], folder: Path) -> None:
    if expected == actual:
        return
    differences = (
        ("missing", sorted(expected.keys() - actual.keys())),
        ("extra", sorted(actual.keys() - expected.keys())),
        ("modified", sorted(name for name in expected.keys() & actual.keys() if expected[name] != actual[name])),
    )
    detail = "; ".join(f"{kind}: {', '.join(paths)}" for kind, paths in differences if paths)
    raise ValueError(f"Modified or untracked files; preserve existing files: {folder} ({detail})")


def verified(folder: Path, *, shared: Path | None = None, installed: bool = False) -> dict[str, str]:
    files = read_manifest(folder)
    actual = snapshot(folder, installed_files=files if installed or shared is not None else ())
    expected_shared = shared_files(files)
    if shared is not None and expected_shared:
        if (folder / "shared").exists():
            raise ValueError(f"Unexpected embedded shared resources; preserve existing files: {folder / 'shared'}")
        shared_snapshot = snapshot(shared, installed_files=expected_shared, exclude_manifest=False)
        check_files(expected_shared, shared_snapshot, shared)
        actual.update({f"shared/{name}": value for name, value in shared_snapshot.items()})
    elif shared is not None and (shared.exists() or linked(shared)):
        raise ValueError(f"Unexpected shared installation; preserve existing files: {shared}")
    check_files(files, actual, folder)
    required = {"SKILL.md", "scripts/govern.py"}
    required.add("shared/sdd/references/delegation.md" if expected_shared else "assets/repo-payload.zip")
    if not required <= actual.keys():
        raise ValueError(f"Incomplete skill: {folder}")
    return actual


def verify_distribution(folder: Path) -> dict[str, str]:
    files = verified(folder)
    required = {
        "scripts/project_install.py", "scripts/release.py", "shared/sdd/references/delegation.md",
        "agents/openai.yaml", "assets/agents-fragment.md",
        "assets/install.md", WORKFLOW_REVIEW_ROLE,
    }
    for name in sorted(required - files.keys()):
        raise ValueError(f"Incomplete distribution: missing {name}: {folder}")
    if USER_ROLE_ASSET in files:
        raise ValueError(f"Standalone user role is no longer distributed: {USER_ROLE_ASSET}")
    path = folder / WORKFLOW_REVIEW_ROLE
    role = tomllib.loads(path.read_text(encoding="utf-8"))
    if role.get("name") != USER_ROLE or not all(
        isinstance(role.get(key), str) and role[key].strip()
        for key in ("description", "developer_instructions")
    ):
        raise ValueError(f"Invalid distributed workflow role: {path}")
    return files
