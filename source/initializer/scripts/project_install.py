"""Host-local installation lock and restartable file recovery (standard library)."""
from __future__ import annotations

import base64
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess

RECOVERY = ".sdd-init-recovery"
WORKFLOW_LINK = ".agents/sdd-workflow"
COPILOT_WORKFLOW_LINK = ".github/sdd-workflow"
LEGACY_WORKFLOW_LINK = ".agents/skills/sdd-workflow"
PROJECT_SKILLS = (
    "sdd-architecture", "sdd-bugfix", "sdd-deliver", "sdd-develop", "sdd-refactor", "sdd-test-loop",
)
SKILL_LINKS = tuple(f".agents/skills/{name}" for name in PROJECT_SKILLS)
PROJECT_ROLES = (
    "review-prompt", "sdd-architect", "sdd-product-manager",
    "sdd-coder", "sdd-devops", "sdd-doc-consistency",
)
COPILOT_ROLE_FILES = tuple(f".github/agents/{name}.agent.md" for name in PROJECT_ROLES)
COPILOT_LINKS = (COPILOT_WORKFLOW_LINK,)
INSTALL_LINKS = (WORKFLOW_LINK, COPILOT_WORKFLOW_LINK, *SKILL_LINKS, LEGACY_WORKFLOW_LINK)
LOCK = ".sdd-init.lock"
STATE = ".sdd-init-state.json"
FILES = ("AGENTS.md", ".codex/config.toml", ".gitignore", STATE, "AGENTS.override.md",
         *COPILOT_ROLE_FILES)


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
        if path != target and path.exists() and not path.is_dir():
            raise ValueError(f"Not an installation directory: {path}")
    if target == root or root.resolve() not in target.resolve().parents:
        raise ValueError(f"Path outside installation: {target}")
    return target


def link_path(root: Path, relative: str) -> Path:
    parts = Path(relative).parts
    is_skill = len(parts) >= 3 and parts[:2] == (".agents", "skills")
    is_role = len(parts) == 3 and parts[:2] == (".codex", "agents") and Path(parts[2]).suffix == ".toml"
    if relative not in INSTALL_LINKS and not (is_skill or is_role):
        raise ValueError(f"Invalid installation link: {relative}")
    relative = Path(relative)
    parent = safe_path(root, relative.parent.as_posix())
    if parent.exists() and not parent.is_dir():
        raise ValueError(f"Not an installation directory: {parent}")
    return parent / relative.name


def workflow_path(root: Path) -> Path:
    return link_path(root, WORKFLOW_LINK)


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


def publish_workflow_link(stage: Path, path: Path):
    """Publish without replacing an entry created after the final conflict check."""
    if os.name == "nt":
        # Windows rename refuses an existing destination, including junctions.
        os.rename(stage, path)
    else:
        # Link the symlink inode, not its directory target. Unlike POSIX rename,
        # link is atomic and refuses any existing destination (even a symlink).
        os.link(stage, path, follow_symlinks=False)
        stage.unlink()


def link_snapshot(path: Path, *, logical_parent: Path | None = None) -> dict | None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if not linked(path):
        inventory = entry_inventory(path)
        return {"target": None, "device": info.st_dev, "inode": info.st_ino,
                "content": inventory_digest(inventory), "inventory": inventory}
    if logical_parent is None:
        target = workflow_target(path)
    else:
        target = (logical_parent / os.readlink(path).removeprefix("\\\\?\\")).resolve()
    return {"target": str(target), "device": info.st_dev, "inode": info.st_ino}


def entry_inventory(path: Path) -> dict:
    entries, pending = {}, [(path, ".")]
    while pending:
        current, relative = pending.pop()
        info = current.lstat()
        mode = stat.S_IMODE(info.st_mode)
        if linked(current):
            entries[relative] = ["link", mode, os.readlink(current)]
        elif current.is_dir():
            entries[relative] = ["directory", mode]
            for child in current.iterdir():
                name = child.name if relative == "." else f"{relative}/{child.name}"
                pending.append((child, name))
        elif current.is_file():
            entries[relative] = ["file", mode, hashlib.sha256(current.read_bytes()).hexdigest()]
        else:
            raise ValueError(f"Unsupported installation entry: {current}")
    return entries


def inventory_digest(entries: dict) -> str:
    return hashlib.sha256(json.dumps(entries, sort_keys=True, ensure_ascii=True).encode("utf-8")).hexdigest()


def remove_workflow_link(path: Path):
    # Never recurse or use a directory-tree remover on shared resources.
    workflow_target(path)
    if path.is_symlink():
        path.unlink()
    else:
        path.rmdir()


def plan_links(root: Path, shared: Path, *, copilot: bool = False) -> list[tuple[Path, dict | None, Path | None]]:
    shared = shared.resolve()
    if shared.is_relative_to(root.resolve()):
        raise ValueError(f"Shared resources must be outside the project: {shared}")
    targets = {WORKFLOW_LINK: shared,
               **{relative: shared / "skills" / Path(relative).name for relative in SKILL_LINKS},
               LEGACY_WORKFLOW_LINK: None}
    if copilot:
        targets[COPILOT_WORKFLOW_LINK] = shared
    result = []
    for relative, target in targets.items():
        path = link_path(root, relative)
        before = link_snapshot(path)
        result.append((path, before, target))
    return result


def link_is_current(before: dict | None, target: Path | None) -> bool:
    if target is None:
        return before is None
    return before is not None and before["target"] == str(target.resolve())


def should_displace(entry: dict) -> bool:
    before = entry["before"]
    return before is not None and (before["target"] is None or entry["target"] is not None
                                   or entry["path"] != LEGACY_WORKFLOW_LINK)


@contextmanager
def project_lock(root: Path):
    # Keep the inode stable: deleting an unlocked file could split concurrent
    # waiters across two locks. The project path is independent of TEMP and
    # user session; the one-byte metadata file remains after unlock.
    path = safe_path(root, LOCK)
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


def clean(folder: Path, journal: dict | None = None):
    # Delete only our known regular files, never recursively delete this path.
    for name in ("stage", "journal.json"):
        path = folder / name
        if linked(path) or (path.exists() and not path.is_file()):
            raise ValueError(f"Unexpected recovery file: {path}")
    for path in folder.iterdir():
        if path.name in {"stage", "journal.json"}:
            continue
        if (journal is None or not path.name.startswith("old-") or not path.name[4:].isdigit()
                or int(path.name[4:]) >= len(journal.get("links", []))):
            raise ValueError(f"Unexpected recovery contents: {path}")
        entry = journal["links"][int(path.name[4:])]
        before = entry["before"]
        original_parent = (Path(journal["root"]) / entry["path"]).parent
        actual = link_snapshot(path, logical_parent=original_parent)
        if before is None or actual is None:
            raise ValueError(f"External modification; preserve installation backup: {path}")
        if before["target"] is not None:
            if actual != before:
                raise ValueError(f"External modification; preserve installation backup: {path}")
            remove_workflow_link(path)
        elif (actual["target"] is not None or any(actual[key] != before[key] for key in ("device", "inode"))
              or any(before["inventory"].get(name) != value for name, value in actual["inventory"].items())):
            raise ValueError(f"External modification; preserve installation backup: {path}")
        elif path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
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
    if (not isinstance(journal, dict) or journal.get("version") not in (1, 2, 3)
            or journal.get("root") != str(root.resolve())
            or journal.get("state") not in ("prepared", "committed")
            or not isinstance(journal.get("files"), list)
            or not isinstance(journal.get("directories"), list)):
        raise ValueError("Invalid recovery journal")
    seen = set()
    for entry in journal["files"]:
        path = safe_path(root, entry["path"])
        if (path in seen or RECOVERY in path.relative_to(root).parts
                or (journal["version"] >= 2 and entry["path"] not in FILES)
                or type(entry["mode"]) is not int or not 0 <= entry["mode"] <= 0o7777):
            raise ValueError(f"Invalid recovery entry: {path}")
        seen.add(path)
        decode(entry["before"])
        if decode(entry["after"]) is None:
            raise ValueError(f"Missing installed bytes: {path}")
    if journal["version"] == 3:
        if "workflow_target" in journal or "link_started" in journal:
            raise ValueError("Mixed recovery journal versions")
        validate_links(root, journal, seen)
    elif journal.get("workflow_target") is not None:
        validate_external_target(root, journal["workflow_target"])
        seen.add(link_path(root, LEGACY_WORKFLOW_LINK))
    for directory in journal["directories"]:
        path = safe_path(root, directory)
        if not any(path in file.parents for file in seen):
            raise ValueError(f"Invalid recovery directory: {path}")
    if journal["version"] >= 2:
        started = journal.get("started")
        count = len(journal["files"])
        if type(started) is not int or not 0 <= started <= count:
            raise ValueError("Invalid recovery file progress")
        if journal["version"] == 2:
            if not isinstance(journal.get("link_started"), bool) or (
                    journal["link_started"] and (not journal.get("workflow_target") or started != count)):
                raise ValueError("Invalid recovery link progress")
            complete = journal["link_started"] == bool(journal.get("workflow_target"))
        else:
            if journal["links_started"] and started != count:
                raise ValueError("Invalid recovery link progress")
            complete = journal["links_started"] == len(journal["links"])
        if journal["state"] == "committed" and (started != count or not complete):
            raise ValueError("Incomplete committed recovery journal")
    return journal


def validate_external_target(root: Path, raw: str) -> Path:
    target = Path(raw)
    if not target.is_absolute() or target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Invalid shared directory in recovery journal: {target}")
    return target


def validate_snapshot(root: Path, snapshot: dict | None, *, allow_project_target: bool = False):
    if snapshot is None:
        return
    if (not isinstance(snapshot, dict) or set(snapshot) not in ({"target", "device", "inode"},
                                                                {"target", "device", "inode", "content", "inventory"})
            or any(type(snapshot[key]) is not int or snapshot[key] < 0 for key in ("device", "inode"))):
        raise ValueError("Invalid recovery link identity")
    if snapshot["target"] is None:
        if (not allow_project_target or not isinstance(snapshot.get("inventory"), dict)
                or not isinstance(snapshot.get("content"), str)
                or snapshot["content"] != inventory_digest(snapshot["inventory"])):
            raise ValueError("Invalid recovery entry identity")
        return
    if "content" in snapshot:
        raise ValueError("Invalid recovery link identity")
    if allow_project_target:
        if not isinstance(snapshot["target"], str) or not Path(snapshot["target"]).is_absolute():
            raise ValueError("Invalid recovery link target")
    else:
        validate_external_target(root, snapshot["target"])


def validate_links(root: Path, journal: dict, seen: set):
    links, started = journal.get("links"), journal.get("links_started")
    if not isinstance(links, list) or type(started) is not int or not 0 <= started <= len(links):
        raise ValueError("Invalid recovery links")
    for index, entry in enumerate(links):
        path = link_path(root, entry["path"])
        if path in seen:
            raise ValueError(f"Duplicate recovery link: {path}")
        seen.add(path)
        for key in ("before", "after", "restored"):
            validate_snapshot(root, entry[key], allow_project_target=key != "after")
        target = entry["target"]
        if target is not None:
            validate_external_target(root, target)
            if entry["after"] is not None and entry["after"]["target"] != target:
                raise ValueError("Invalid staged link target")
            if entry["restored"] is not None and (entry["before"] is None
                    or entry["restored"]["target"] != entry["before"]["target"]):
                raise ValueError("Invalid restored link target")
        elif (entry["before"] is None
              or entry["after"] is not None or (entry["restored"] is not None
                  and entry["restored"]["target"] != entry["before"]["target"])):
            raise ValueError("Invalid installation entry removal")
        if index >= started and (entry["after"] is not None or entry["restored"] is not None):
            raise ValueError("Invalid recovery link progress")
        if journal["state"] == "committed" and target is not None and entry["after"] is None:
            raise ValueError("Unpublished committed link")


def staged_link(root: Path, index: int) -> Path:
    # Only the final component may be a link. The recovery directory stays local.
    return safe_path(root, RECOVERY) / f"link-{index}"


def displaced_entry(root: Path, index: int) -> Path:
    return safe_path(root, RECOVERY) / f"old-{index}"


def check_recovery_link(root: Path, index: int, entry: dict):
    path = link_path(root, entry["path"])
    if link_snapshot(path) not in (entry["before"], entry["after"], entry["restored"]):
        raise ValueError(f"External modification; preserve link: {path}")
    stage = staged_link(root, index)
    backup = displaced_entry(root, index)
    saved = link_snapshot(backup, logical_parent=path.parent)
    if saved is not None and (not should_displace(entry) or saved != entry["before"]):
        raise ValueError(f"External modification; preserve installation backup: {backup}")
    snapshot = link_snapshot(stage)
    if snapshot is not None:
        candidates = [(entry["target"], entry["after"])] if entry["target"] else []
        if entry["before"] is not None and entry["before"]["target"] is not None:
            candidates.append((entry["before"]["target"], entry["restored"]))
        if not any(snapshot["target"] == target and (recorded is None or snapshot == recorded)
                   for target, recorded in candidates):
            raise ValueError(f"External modification; preserve staged link: {stage}")


def check_recovery_links(root: Path, journal: dict):
    for index, entry in enumerate(journal["links"][:journal["links_started"]]):
        check_recovery_link(root, index, entry)


def restore_links(root: Path, folder: Path, journal: dict):
    for index in reversed(range(journal["links_started"])):
        entry = journal["links"][index]
        path, stage = link_path(root, entry["path"]), staged_link(root, index)
        check_recovery_link(root, index, entry)
        current = link_snapshot(path)
        if entry["before"] is None:
            if current is not None:
                remove_workflow_link(path)
        elif should_displace(entry):
            backup = displaced_entry(root, index)
            if current != entry["before"]:
                if link_snapshot(backup, logical_parent=path.parent) != entry["before"]:
                    raise ValueError(f"Missing or modified installation backup: {backup}")
                if current is not None:
                    remove_workflow_link(path)
                if link_snapshot(path) is not None:
                    raise ValueError(f"External modification; preserve entry: {path}")
                backup.rename(path)
            elif link_snapshot(backup, logical_parent=path.parent) is not None:
                raise ValueError(f"Unexpected duplicate installation backup: {backup}")
        elif current != entry["before"]:
            if current is not None:
                remove_workflow_link(path)
            staged = link_snapshot(stage)
            if staged is not None and staged["target"] != entry["before"]["target"]:
                remove_workflow_link(stage)
            if link_snapshot(stage) is None:
                create_workflow_link(stage, Path(entry["before"]["target"]))
            entry["restored"] = link_snapshot(stage)
            save(folder, journal)
            # Recheck after journal I/O; never replace an external entry.
            if link_snapshot(path) is not None:
                raise ValueError(f"External modification; preserve link: {path}")
            publish_workflow_link(stage, path)
        if link_snapshot(stage) is not None:
            remove_workflow_link(stage)


def recover(root: Path):
    folder = root / RECOVERY
    try:
        safe_path(root, RECOVERY)
        if not folder.exists():
            return False
        journal = load(root, folder)
        if journal is None or journal["state"] == "committed":
            if journal is not None and journal["version"] == 3:
                for entry in journal["links"]:
                    path = link_path(root, entry["path"])
                    if link_snapshot(path) != entry["after"]:
                        raise ValueError(f"External modification; preserve link: {path}")
            clean(folder, journal)
            return True
        entries = journal["files"][:journal.get("started", len(journal["files"]))]
        link_started = journal.get("workflow_target") is not None and journal.get("link_started", True)
        # Validate the attempted writes before touching any files. External edits are
        # conflicts, including edits to AGENTS outside the managed blocks.
        for entry in entries:
            path = safe_path(root, entry["path"])
            if content(path) not in (decode(entry["before"]), decode(entry["after"])):
                raise ValueError(f"External modification; preserve file: {path}")
        if journal["version"] == 3:
            check_recovery_links(root, journal)
            restore_links(root, folder, journal)
        if link_started:
            # Historical journals always refer to the old nested anchor.
            path = link_path(root, LEGACY_WORKFLOW_LINK)
            current_target = workflow_target(path)
            if current_target is not None:
                if current_target != Path(journal["workflow_target"]).resolve():
                    raise ValueError(f"External modification; preserve link: {path}")
                remove_workflow_link(path)
        for entry in reversed(entries):
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
        touched = [root / entry["path"] for entry in entries]
        if link_started:
            touched.append(root / LEGACY_WORKFLOW_LINK)
        if journal["version"] == 3:
            touched.extend(root / entry["path"] for entry in journal["links"][:journal["links_started"]])
        for relative in reversed(journal["directories"]):
            path = safe_path(root, relative)
            if any(path in target.parents for target in touched) and path.is_dir() and not any(path.iterdir()):
                path.rmdir()
        clean(folder)
        print(f"RECOVERED {root}")
        return True
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError(
            f"Recovery blocked: {error}. 保留恢复记录: {folder}; "
            "核对受影响路径并解除冲突后运行 recover 或重试 init，禁止删除记录后强制覆盖。"
        ) from error


def apply(root: Path, files: list[tuple[Path, bytes, bytes | None]], *,
          shared: Path | None = None,
          links: list[tuple[Path, dict | None, Path | None]] | None = None,
          guard=None, verify=None):
    """Caller holds project_lock and has recovered any prior operation.

    Link plans include unchanged entries as guards. New links are staged on the
    same filesystem so their identity is journaled before atomic publication.
    """
    if shared is not None and links is not None:
        raise ValueError("Specify shared or links, not both")
    if guard:
        guard()
    links = plan_links(root, shared) if shared is not None else (links or [])
    folder = safe_path(root, RECOVERY)
    entries, link_entries, directories = [], [], set()
    for target, data, before in files:
        target = safe_path(root, target.relative_to(root).as_posix())
        if content(target) != before:
            raise ValueError(f"File changed after preflight; preserve file: {target}")
        if data == before:
            continue
        entries.append({"path": target.relative_to(root).as_posix(),
                        "before": encode(before), "after": encode(data),
                        "mode": stat.S_IMODE(target.stat().st_mode) if before is not None else 0o644})
    for path, before, target in links:
        relative = path.relative_to(root).as_posix()
        path = link_path(root, relative)
        if link_snapshot(path) != before:
            raise ValueError(f"Link changed after preflight; preserve link: {path}")
        desired = str(target.resolve()) if target is not None else None
        if link_is_current(before, target):
            continue
        link_entries.append({"path": relative, "before": before, "target": desired,
                             "after": None, "restored": None})
    if not entries and not link_entries:
        if verify:
            verify()
        return
    targets = [root / entry["path"] for entry in [*entries, *link_entries]]
    for target in targets:
        for parent in target.parents:
            if parent == root:
                break
            if not parent.exists():
                directories.add(parent.relative_to(root).as_posix())
    journal = {"version": 3, "root": str(root.resolve()), "state": "prepared",
               "files": entries, "started": 0, "links": link_entries, "links_started": 0,
               "directories": sorted(directories, key=lambda p: (len(Path(p).parts), p))}
    # Validate the complete plan before publishing a journal or changing targets.
    validate_links(root, journal, set())
    folder.mkdir(mode=0o700)
    try:
        save(folder, journal)
        for index, entry in enumerate(entries, 1):
            target = safe_path(root, entry["path"])
            if content(target) != decode(entry["before"]):
                raise ValueError(f"File changed during installation: {target}")
            journal["started"] = index
            save(folder, journal)
            target.parent.mkdir(parents=True, exist_ok=True)
            replace_file(folder, target, decode(entry["after"]), entry["mode"])
        for index, entry in enumerate(link_entries):
            path = link_path(root, entry["path"])
            if link_snapshot(path) != entry["before"]:
                raise ValueError(f"Link changed during installation: {path}")
            journal["links_started"] = index + 1
            save(folder, journal)
            if entry["target"] is not None:
                stage = staged_link(root, index)
                create_workflow_link(stage, Path(entry["target"]))
                entry["after"] = link_snapshot(stage)
                if entry["after"] is None or entry["after"]["target"] != entry["target"]:
                    raise ValueError(f"Unexpected staged link target: {stage}")
                save(folder, journal)
                path.parent.mkdir(parents=True, exist_ok=True)
                if link_snapshot(path) != entry["before"]:
                    raise ValueError(f"Link changed during installation: {path}")
                if entry["before"] is not None:
                    if should_displace(entry):
                        backup = displaced_entry(root, index)
                        if link_snapshot(backup) is not None:
                            raise ValueError(f"Unexpected installation backup: {backup}")
                        path.rename(backup)
                    else:
                        remove_workflow_link(path)
                publish_workflow_link(stage, path)
            else:
                if link_snapshot(path) != entry["before"]:
                    raise ValueError(f"Link changed during installation: {path}")
                if should_displace(entry):
                    backup = displaced_entry(root, index)
                    if link_snapshot(backup) is not None:
                        raise ValueError(f"Unexpected installation backup: {backup}")
                    path.rename(backup)
                else:
                    remove_workflow_link(path)
        if verify:
            verify()
        # Detect replacement even by a link to the same target, before commit.
        changed = {entry["path"]: entry["after"] for entry in link_entries}
        for path, before, _ in links:
            expected = changed.get(path.relative_to(root).as_posix(), before)
            if link_snapshot(link_path(root, path.relative_to(root).as_posix())) != expected:
                raise ValueError(f"External modification; preserve link: {path}")
        journal["state"] = "committed"
        save(folder, journal)
    except BaseException:
        # A killed process cannot run this block; the next init replays the same
        # recovery. BaseException also handles an interactive cancellation.
        recover(root)
        raise
    clean(folder, journal)
