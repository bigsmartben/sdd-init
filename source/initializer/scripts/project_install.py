"""Host-local installation lock and restartable file recovery (standard library)."""
from __future__ import annotations

import base64
from contextlib import contextmanager
import json
import os
from pathlib import Path
import stat
import subprocess

RECOVERY = ".sdd-init-recovery"
WORKFLOW_LINK = ".agents/skills/sdd-workflow"


def linked(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def safe_path(root: Path, relative: str) -> Path:
    rel = Path(relative)
    if not relative or rel.is_absolute() or rel.drive or ".." in rel.parts:
        raise ValueError(f"Invalid installation path: {relative}")
    target = root / rel
    for path in (target, *target.parents):
        if path == root:
            break
        if linked(path):
            raise ValueError(f"Linked installation path: {path}")
    if target == root or root.resolve() not in target.resolve().parents:
        raise ValueError(f"Path outside installation: {target}")
    return target


def workflow_path(root: Path) -> Path:
    relative = Path(WORKFLOW_LINK)
    return safe_path(root, relative.parent.as_posix()) / relative.name


def workflow_target(path: Path) -> Path | None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if not (stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", None) == 0xA0000003):
        raise ValueError(f"Existing path is not an SDD directory link; preserve it: {path}")
    # readlink works even during a user-level directory replacement or after a move.
    target = os.readlink(path).removeprefix("\\\\?\\")
    return (path.parent / target).resolve()


def create_workflow_link(path: Path, target: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        path.symlink_to(target, target_is_directory=True)
        return
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
         "New-Item -ItemType Junction -Path $env:SDD_LINK_PATH "
         "-Target $env:SDD_LINK_TARGET -ErrorAction Stop | Out-Null"],
        env=dict(os.environ, SDD_LINK_PATH=str(path), SDD_LINK_TARGET=str(target)),
        capture_output=True, text=True, errors="replace", check=False,
    )
    if result.returncode:
        raise OSError(f"Cannot create junction {path}: {result.stderr.strip()}")


@contextmanager
def project_lock(root: Path):
    # Keep the inode stable: deleting an unlocked file could split concurrent
    # waiters across two locks. The project path is independent of TEMP and
    # user session; the one-byte metadata file remains after unlock.
    path = safe_path(root, ".sdd-init.lock")
    with os.fdopen(os.open(path, os.O_RDWR | os.O_CREAT, 0o600), "r+b") as handle:
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise ValueError(f"已有安装任务 / installation in progress: {root}") from error
        try:
            handle.seek(0)
            data = handle.read()
            if data not in (b"", b"\0"):
                raise ValueError(f"Unexpected lock contents; preserve file: {path}")
            if not data:
                handle.seek(0)
                handle.write(b"\0")
                handle.flush()
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def content(path: Path) -> bytes | None:
    if path.exists() and not path.is_file():
        raise ValueError(f"Not a regular file: {path}")
    return path.read_bytes() if path.exists() else None


def encode(data: bytes | None) -> str | None:
    return None if data is None else base64.b64encode(data).decode("ascii")


def decode(data: str | None) -> bytes | None:
    return None if data is None else base64.b64decode(data, validate=True)


def replace_file(folder: Path, path: Path, data: bytes, mode: int = 0o644):
    """Staging stays in the journal folder; crashes never leave partial targets."""
    staged = folder / "stage"
    if linked(staged):
        raise ValueError(f"Linked stage path: {staged}")
    with staged.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.chmod(staged, mode)
    os.replace(staged, path)


def save(folder: Path, journal: dict):
    replace_file(folder, folder / "journal.json",
                 json.dumps(journal, ensure_ascii=True).encode("utf-8"), 0o600)


def clean(folder: Path):
    # Delete only our known regular files, never recursively delete this path.
    for name in ("stage", "journal.json"):
        path = folder / name
        if linked(path) or (path.exists() and not path.is_file()):
            raise ValueError(f"Unexpected recovery file: {path}")
    if any(p.name not in {"stage", "journal.json"} for p in folder.iterdir()):
        raise ValueError(f"Unexpected recovery contents: {folder}")
    (folder / "stage").unlink(missing_ok=True)
    (folder / "journal.json").unlink(missing_ok=True)
    folder.rmdir()


def load(root: Path, folder: Path) -> dict | None:
    journal_path = safe_path(root, f"{RECOVERY}/journal.json")
    if not journal_path.exists():
        # Initial journal publication did not complete: target writes cannot
        # have started. Only known staging files are eligible for cleanup.
        return None
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    if (not isinstance(journal, dict) or journal.get("version") != 1
            or journal.get("root") != str(root.resolve())
            or journal.get("state") not in ("prepared", "committed")
            or not isinstance(journal.get("files"), list)
            or not isinstance(journal.get("directories"), list)):
        raise ValueError("Invalid recovery journal")
    seen = set()
    for entry in journal["files"]:
        path = safe_path(root, entry["path"])
        if (path in seen or RECOVERY in path.relative_to(root).parts
                or not isinstance(entry["mode"], int)):
            raise ValueError(f"Invalid recovery entry: {path}")
        seen.add(path)
        decode(entry["before"])
        if decode(entry["after"]) is None:
            raise ValueError(f"Missing installed bytes: {path}")
    if journal.get("workflow_target") is not None:
        target = Path(journal["workflow_target"])
        if not target.is_absolute() or target.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"Invalid shared directory in recovery journal: {target}")
        seen.add(workflow_path(root))
    for directory in journal["directories"]:
        path = safe_path(root, directory)
        if not any(path in file.parents for file in seen):
            raise ValueError(f"Invalid recovery directory: {path}")
    return journal


def recover(root: Path):
    folder = safe_path(root, RECOVERY)
    if not folder.exists():
        return
    try:
        journal = load(root, folder)
        if journal is None or journal["state"] == "committed":
            clean(folder)
            return
        # Validate the entire set before touching any files. External edits are
        # conflicts, including edits to AGENTS outside the managed blocks.
        for entry in journal["files"]:
            path = safe_path(root, entry["path"])
            if content(path) not in (decode(entry["before"]), decode(entry["after"])):
                raise ValueError(f"External modification; preserve file: {path}")
        if journal.get("workflow_target") is not None:
            path = workflow_path(root)
            current_target = workflow_target(path)
            if current_target is not None:
                if current_target != Path(journal["workflow_target"]).resolve():
                    raise ValueError(f"External modification; preserve link: {path}")
                # Remove the directory entry only. Never walk into the shared directory.
                if path.is_symlink():
                    path.unlink()
                else:
                    path.rmdir()
        for entry in reversed(journal["files"]):
            path = safe_path(root, entry["path"])
            before, after = decode(entry["before"]), decode(entry["after"])
            current = content(path)
            if current == before:
                continue
            if current != after:
                raise ValueError(f"External modification; preserve file: {path}")
            if before is None:
                path.unlink()
            else:
                replace_file(folder, path, before, entry["mode"])
        for relative in reversed(journal["directories"]):
            path = safe_path(root, relative)
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()
        clean(folder)
        print(f"RECOVERED {root}")
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError(
            f"Recovery blocked: {error}. 保留恢复记录: {folder}; "
            "核对受影响路径并解除冲突后重新执行 init，禁止删除记录后强制覆盖。"
        ) from error


def apply(root: Path, changes: list[tuple[Path, bytes, bytes | None]], *, shared: Path | None = None):
    """Caller holds project_lock and has recovered any prior operation."""
    if not changes and shared is None:
        return
    folder = safe_path(root, RECOVERY)
    entries, directories = [], set()
    for target, data, before in changes:
        target = safe_path(root, target.relative_to(root).as_posix())
        if content(target) != before:
            raise ValueError(f"File changed after preflight; preserve file: {target}")
        entries.append({"path": target.relative_to(root).as_posix(),
                        "before": encode(before), "after": encode(data),
                        "mode": stat.S_IMODE(target.stat().st_mode) if before is not None else 0o644})
    targets = [target for target, _, _ in changes]
    if shared is not None:
        path = workflow_path(root)
        if workflow_target(path) is not None:
            raise ValueError(f"Workflow link changed after preflight: {path}")
        targets.append(path)
    for target in targets:
        for parent in target.parents:
            if parent == root:
                break
            if not parent.exists():
                directories.add(parent.relative_to(root).as_posix())
    journal = {"version": 1, "root": str(root.resolve()), "state": "prepared",
               "files": entries,
               "directories": sorted(directories, key=lambda p: (len(Path(p).parts), p))}
    if shared is not None:
        journal["workflow_target"] = str(shared)
    folder.mkdir(mode=0o700)
    try:
        save(folder, journal)
        for entry in entries:
            target = safe_path(root, entry["path"])
            if content(target) != decode(entry["before"]):
                raise ValueError(f"File changed during installation: {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            replace_file(folder, target, decode(entry["after"]), entry["mode"])
        if shared is not None:
            path = workflow_path(root)
            if workflow_target(path) is not None:
                raise ValueError(f"Workflow link changed during installation: {path}")
            create_workflow_link(path, shared)
            if workflow_target(path) != shared:
                raise ValueError(f"Unexpected workflow link target: {path}")
        journal["state"] = "committed"
        save(folder, journal)
    except BaseException:
        # A killed process cannot run this block; the next init replays the same
        # recovery. BaseException also handles an interactive cancellation.
        recover(root)
        raise
    clean(folder)
