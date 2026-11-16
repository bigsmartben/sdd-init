"""Install the initializer and workflow resources; retire owned legacy user roles."""
from __future__ import annotations

from contextlib import nullcontext
import json
import os
from pathlib import Path
import re
import shutil

from .release import (
    MANIFEST, USER_ROLE, USER_ROLE_ASSET, check_files, digest, linked, manifest_data,
    recovery_directory, shared_directory,
    shared_files, snapshot, user_lock, verified, verify_distribution,
)

ROLE_LOCK = f".sdd-init-{USER_ROLE}.lock"
ROLE_RECOVERY_PREFIX = f".sdd-init-{USER_ROLE}-recovery-"


def unlinked_directory(path: Path) -> Path:
    absolute = Path(os.path.abspath(path.expanduser()))
    for path in (absolute, *absolute.parents):
        if linked(path):
            raise ValueError(f"Linked installation path is not supported: {path}")
        if path.exists() and not path.is_dir():
            raise ValueError(f"Invalid installation directory: {path}")
    return absolute


def locations(skills_dir: Path) -> tuple[Path, Path, Path]:
    skills_dir = unlinked_directory(skills_dir)
    return skills_dir / "sdd-init", shared_directory(skills_dir), recovery_directory(skills_dir)


def role_location(agents_dir: Path, target: Path, shared: Path, folder: Path) -> Path:
    agents_dir = unlinked_directory(agents_dir)
    role = agents_dir / f"{USER_ROLE}.toml"
    for role_path in (role, role_recovery_directory(role, target), agents_dir / ROLE_LOCK):
        if any(role_path.is_relative_to(path) or path.is_relative_to(role_path)
               for path in (target, shared, folder)):
            raise ValueError(f"User role and Skill installation paths overlap: {role_path}, {target}")
    return role


def legacy_role(target: Path, shared: Path, folder: Path, agents_dir: Path | None = None) -> Path | None:
    journal = folder / "journal.json"
    if folder.exists() or linked(folder):
        if linked(folder) or not folder.is_dir() or linked(journal):
            raise ValueError(f"Invalid recovery directory or journal: {folder}")
        try:
            record = json.loads(journal.read_text(encoding="utf-8")) if journal.is_file() else {}
        except (OSError, ValueError) as error:
            raise ValueError(f"Recovery blocked: {error}. Preserve {folder}; review the journal before retrying.") from error
        owner = record.get("role") if isinstance(record, dict) else None
    else:
        owner = manifest_data(target).get("user_role_path") if target.exists() or linked(target) else None
    if owner is None:
        return None
    if not isinstance(owner, str) or not Path(owner).is_absolute() or Path(owner).name != f"{USER_ROLE}.toml":
        raise ValueError(f"Invalid managed user role path: {owner!r}")
    role = role_location(Path(owner).parent, target, shared, folder)
    if agents_dir is not None and role_location(agents_dir, target, shared, folder) != role:
        raise ValueError(f"Managed user role is {role}; use its original --agents-dir")
    return role


def role_recovery_directory(role: Path, target: Path) -> Path:
    # The same target owns the same marker after restart. Other installations
    # sharing this role directory can see the marker even after a process dies.
    owner = digest(os.fsencode(os.path.normcase(target)))
    return role.parent / f"{ROLE_RECOVERY_PREFIX}{owner}"


def check_pending_role_recovery(role: Path) -> None:
    for folder in sorted(role.parent.glob(f"{ROLE_RECOVERY_PREFIX}*")):
        raise ValueError(f"Pending user role installation: {folder}. "
                         "Run sdd-init recover with the original Skill and role directories.")


def role_snapshot(path: Path) -> str | None:
    if linked(path):
        raise ValueError(f"Linked user role is not supported: {path}")
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError(f"User role is not a regular file: {path}")
    return digest(path.read_bytes())


def verify_role_snapshot(path: Path, expected: str | None) -> None:
    if role_snapshot(path) != expected:
        raise ValueError(f"External change to user role: {path}")


def verify_role_manifest(manifest: dict, role: Path | None):
    if USER_ROLE_ASSET in manifest["files"]:
        owner = manifest.get("user_role_path")
        if not isinstance(owner, str) or role is None or Path(owner) != role:
            raise ValueError(f"Managed user role path is {owner!r}; use its original --agents-dir "
                             f"(requested {role})")
    elif "user_role_path" in manifest:
        raise ValueError("User role path without managed role in installation manifest")


def verified_installation(target: Path, shared: Path, role: Path | None = None, *,
                          verify_managed_role: bool = True) -> dict[str, str] | None:
    for path in (target, shared):
        if linked(path):
            raise ValueError(f"Linked installation path is not supported: {path}")
    files = None
    if target.exists():
        files = verified(target, shared=shared)
        verify_role_manifest(manifest_data(target), role)
    elif shared.exists():
        raise ValueError(f"Unexpected shared installation; preserve existing files: {shared}")
    if verify_managed_role and files and USER_ROLE_ASSET in files:
        verify_part(role, files, "role", role)
    return files


def parts(target: Path, shared: Path, folder: Path, role: Path | None):
    yield "shared", shared, folder, folder / "stage/shared"
    yield "skill", target, folder, folder / "stage"
    if role is not None:
        recovery = role_recovery_directory(role, target)
        yield "role", role, recovery, recovery / "stage"


def has_part(files: dict[str, str] | None, kind: str) -> bool:
    if files is None:
        return False
    if kind == "role":
        return USER_ROLE_ASSET in files
    return kind == "skill" or bool(shared_files(files))


def verify_part(path: Path, files: dict[str, str], kind: str, role: Path | None):
    if kind == "role":
        if linked(path) or not path.is_file() or digest(path.read_bytes()) != files[USER_ROLE_ASSET]:
            raise ValueError(f"Missing or modified managed user role; preserve existing file: {path}")
        return
    if kind == "skill":
        manifest = manifest_data(path)
        if manifest["files"] != files:
            raise ValueError(f"External change to release manifest: {path / MANIFEST}")
        verify_role_manifest(manifest, role)
        expected = {name: value for name, value in files.items() if not name.startswith("shared/")}
    else:
        expected = shared_files(files)
    check_files(expected, snapshot(path, installed_files=expected, exclude_manifest=kind == "skill"), path)


def save(folder: Path, record: dict):
    pending = folder / "journal.tmp"
    if linked(pending) or linked(folder / "journal.json"):
        raise ValueError(f"Linked journal at {folder}")
    with pending.open("w", encoding="utf-8") as stream:
        json.dump(record, stream, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())
    pending.replace(folder / "journal.json")


def load(target: Path, folder: Path, role: Path | None = None) -> dict | None:
    if linked(folder) or not folder.is_dir():
        raise ValueError(f"Invalid recovery directory: {folder}")
    names = {"stage", "old-skill", "old-shared", "new-skill", "new-shared", "journal.json", "journal.tmp"}
    for path in folder.iterdir():
        if (path.name not in names or linked(path)
                or (path.name.startswith("journal.") and not path.is_file())):
            raise ValueError(f"Unexpected recovery contents: {path}")
    journal = folder / "journal.json"
    if not journal.exists():
        if any(path.name != "journal.tmp" for path in folder.iterdir()):
            raise ValueError(f"Missing recovery journal: {journal}")
        return None
    record = json.loads(journal.read_text(encoding="utf-8"))
    keys = {"schema_version", "target", "state", "before", "after"}
    schema = record.get("schema_version") if isinstance(record, dict) else None
    if schema in (2, 3, 4):
        keys.add("role")
    if schema == 4:
        keys.add("role_before")
    if (schema not in (1, 2, 3, 4) or set(record) != keys
            or record.get("target") != str(target)
            or record.get("state") not in {"staging", "prepared", "committed", "rolled-back"}):
        raise ValueError(f"Invalid recovery journal: {journal}")
    if schema in (2, 3, 4) and (not isinstance(record["role"], str) or role is None or Path(record["role"]) != role):
        raise ValueError(f"Pending installation targets user role {record['role']!r}; "
                         f"recover with its original --agents-dir (requested {role})")
    if record["state"] == "staging" and any(path.name.startswith(("old-", "new-")) for path in folder.iterdir()):
        raise ValueError(f"Unexpected publication during staging: {folder}")
    for key in ("before", "after"):
        files = record[key]
        if key == "before" and files is None:
            continue
        if (not isinstance(files, dict) or not {"SKILL.md", "scripts/govern.py"} <= files.keys()
                or not all(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)
                           for value in files.values())
                or (schema == 1 and USER_ROLE_ASSET in files)):
            raise ValueError(f"Invalid release data in journal: {journal}")
    if not shared_files(record["after"]) or (schema == 2 and USER_ROLE_ASSET not in record["after"]):
        raise ValueError(f"Incomplete release data in journal: {journal}")
    if schema in (3, 4) and (not has_part(record["before"], "role") or has_part(record["after"], "role")):
        raise ValueError(f"Invalid user role retirement in journal: {journal}")
    if schema == 4 and record["role_before"] is not None and (
            not isinstance(record["role_before"], str) or not re.fullmatch(r"[0-9a-f]{64}", record["role_before"])):
        raise ValueError(f"Invalid user role snapshot in journal: {journal}")
    return record


def clean(folder: Path):
    # All children are installer-owned. Keep the journal until the staged or
    # backed-up bytes have been removed so interrupted cleanup can be retried.
    resolved = folder.resolve()
    if linked(folder) or resolved != folder.parent.resolve() / folder.name:
        raise ValueError(f"Unsafe recovery directory: {folder}")
    for path in folder.iterdir():
        if linked(path):
            raise ValueError(f"Unexpected linked recovery path: {path}")
        if path.name in {"stage", "old-skill", "old-shared", "new-skill", "new-shared"}:
            if not path.is_dir() or path.resolve() != resolved / path.name:
                raise ValueError(f"Unexpected recovery file: {path}")
            shutil.rmtree(path)
        elif path.name not in {"journal.json", "journal.tmp"}:
            raise ValueError(f"Unexpected recovery contents: {path}")
    (folder / "journal.tmp").unlink(missing_ok=True)
    (folder / "journal.json").unlink(missing_ok=True)
    folder.rmdir()


def role_recovery_files(folder: Path, *, staging: bool = False):
    if not (folder.exists() or linked(folder)):
        return []
    if linked(folder) or not folder.is_dir():
        raise ValueError(f"Invalid user role recovery directory: {folder}")
    paths = list(folder.iterdir())
    names = {"stage"} if staging else {"stage", "old-role"}
    for path in paths:
        if path.name not in names or linked(path) or not path.is_file():
            raise ValueError(f"Unexpected user role recovery file: {path}")
    return paths


def clean_role(folder: Path):
    for path in role_recovery_files(folder):
        path.unlink()
    if folder.exists():
        folder.rmdir()


def role_rollback_paths(role: Path, scratch: Path, before: dict | None, after: dict):
    """Identify the published link to remove and the backup to restore."""
    staged, backup = scratch / "stage", scratch / "old-role"
    if not has_part(after, "role"):
        if staged.exists() or linked(staged):
            raise ValueError(f"Unexpected role staging during retirement: {staged}")
        verify_part(backup if backup.exists() else role, before, "role", role)
        if backup.exists() and (role.exists() or linked(role)):
            if linked(role) or not role.samefile(backup):
                raise ValueError(f"External change to installation target: {role}")
        return None, backup if backup.exists() and not role.exists() else None
    verify_part(staged, after, "role", role)
    had_old = has_part(before, "role")
    if linked(role):
        raise ValueError(f"Externally linked installation target: {role}")
    if not backup.exists() and had_old:
        verify_part(role, before, "role", role)
        return None, None
    if backup.exists():
        if not had_old:
            raise ValueError(f"Unexpected backup: {backup}")
        verify_part(backup, before, "role", role)
    if not role.exists():
        return None, backup if had_old else None
    if had_old and role.samefile(backup):
        # A prior recovery restored the role before being interrupted.
        return None, None
    if not role.samefile(staged):
        raise ValueError(f"External change to installation target: {role}")
    return staged, backup if had_old else None


def retired_role_rollback_path(role: Path, scratch: Path, expected: str | None) -> Path | None:
    staged, backup = scratch / "stage", scratch / "old-role"
    if staged.exists() or linked(staged):
        raise ValueError(f"Unexpected role staging during retirement: {staged}")
    if backup.exists() or linked(backup):
        if expected is None:
            raise ValueError(f"Unexpected user role backup: {backup}")
        verify_role_snapshot(backup, expected)
        if role.exists() or linked(role):
            verify_role_snapshot(role, expected)
            if not role.samefile(backup):
                raise ValueError(f"External change to installation target: {role}")
            return None
        return backup
    verify_role_snapshot(role, expected)
    return None


def recover(target: Path, shared: Path, folder: Path, role: Path | None = None) -> bool:
    if not (folder.exists() or linked(folder)):
        return False
    try:
        record = load(target, folder, role)
        if not record or record["schema_version"] == 1:
            role = None
        if role is not None:
            role_folder = role_recovery_directory(role, target)
            role_recovery_files(role_folder, staging=record["state"] == "staging")
        if record is not None and record["state"] != "staging":
            if record["state"] == "prepared":
                before, after = record["before"], record["after"]
                if record["schema_version"] == 4:
                    remove_role = None
                    restore_role = retired_role_rollback_path(role, role_folder, record["role_before"])
                else:
                    remove_role, restore_role = (role_rollback_paths(role, role_folder, before, after)
                                                 if role is not None else (None, None))
                moves = []
                for kind, path, scratch, staged in parts(target, shared, folder, None):
                    backup = scratch / f"old-{kind}"
                    holding = scratch / f"new-{kind}"
                    had_old = has_part(before, kind)
                    if linked(path):
                        raise ValueError(f"Externally linked installation target: {path}")
                    if backup.exists() and not had_old:
                        raise ValueError(f"Unexpected backup: {backup}")
                    if had_old:
                        verify_part(backup if backup.exists() else path, before, kind, role)
                    if holding.exists():
                        if staged.exists():
                            raise ValueError(f"Unexpected recovered copy: {holding}")
                        verify_part(holding, after, kind, role)
                    if path.exists() and (backup.exists() or not had_old):
                        if holding.exists() or staged.exists():
                            raise ValueError(f"External change to installation target: {path}")
                        verify_part(path, after, kind, role)
                        moves.append((path, holding, after, kind))
                    if backup.exists():
                        moves.append((backup, path, before, kind))
                for source, destination, files, kind in moves:
                    if destination.exists() or linked(destination):
                        raise ValueError(f"External change to recovery destination: {destination}")
                    verify_part(source, files, kind, role)
                    source.rename(destination)
                if remove_role is not None:
                    verify_part(role, after, "role", role)
                    if not role.samefile(remove_role):
                        raise ValueError(f"External change to installation target: {role}")
                    role.unlink()
                if restore_role is not None:
                    if record["schema_version"] == 4:
                        verify_role_snapshot(restore_role, record["role_before"])
                    else:
                        verify_part(restore_role, before, "role", role)
                    os.link(restore_role, role)
                if verified_installation(target, shared, role, verify_managed_role=record["schema_version"] != 4) != before:
                    raise ValueError(f"Unexpected version after recovery: {target}, {shared}")
                if record["schema_version"] == 4:
                    verify_role_snapshot(role, record["role_before"])
                record["state"] = "rolled-back"
                save(folder, record)
            else:
                key = "before" if record["state"] == "rolled-back" else "after"
                if verified_installation(target, shared, role, verify_managed_role=record["schema_version"] != 4) != record[key]:
                    raise ValueError(f"External change after {record['state']}: {target}, {shared}")
                if record["schema_version"] == 4 and record["state"] == "rolled-back":
                    verify_role_snapshot(role, record["role_before"])
                if record["schema_version"] in (3, 4) and record["state"] == "committed" and (role.exists() or linked(role)):
                    raise ValueError(f"External change to retired user role: {role}")
                if record["schema_version"] in (3, 4) and record["state"] == "committed":
                    backup = role_folder / "old-role"
                    if backup.exists() or linked(backup):
                        if record["schema_version"] == 4:
                            if record["role_before"] is None:
                                raise ValueError(f"Unexpected user role backup: {backup}")
                            verify_role_snapshot(backup, record["role_before"])
                        else:
                            verify_part(backup, record["before"], "role", role)
        if role is not None:
            clean_role(role_folder)
        clean(folder)
        return True
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError(
            f"Recovery blocked: {error}. Preserve {folder}; "
            f"review the reported paths, then retry sdd-init recover with the same directories."
        ) from error


def recover_installation(skills_dir: Path, agents_dir: Path | None = None) -> bool:
    target, shared, folder = locations(skills_dir)
    if not (folder.exists() or linked(folder)):
        return False
    role = legacy_role(target, shared, folder, agents_dir)
    with user_lock(target.parent):
        # Old journals precede the user role and may have no role directory yet.
        lock = user_lock(role.parent, name=ROLE_LOCK) if role is not None and role.parent.is_dir() else nullcontext()
        with lock:
            return recover(target, shared, folder, role)


def install(resources: Path, skills_dir: Path, agents_dir: Path | None = None) -> str:
    expected = verify_distribution(resources)
    target, shared, folder = locations(skills_dir)
    role = legacy_role(target, shared, folder, agents_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    lock = user_lock(role.parent, name=ROLE_LOCK) if role is not None and role.parent.is_dir() else nullcontext()
    with user_lock(target.parent), lock:
        recover(target, shared, folder, role)
        before = verified_installation(target, shared, role, verify_managed_role=False)
        if before == expected:
            return "Already current"
        if not has_part(before, "role"):
            role = None
        if role is not None:
            check_pending_role_recovery(role)
        role_before = role_snapshot(role) if role is not None else None
        record = {"schema_version": 1 if role is None else 4, "target": str(target), "state": "staging",
                  "before": before, "after": expected}
        if role is not None:
            record["role"] = str(role)
            record["role_before"] = role_before
        folder.mkdir(mode=0o700)
        try:
            save(folder, record)
            staged = folder / "stage"
            shutil.copytree(resources, staged, symlinks=True)
            if verified(staged) != expected or verified_installation(target, shared, role, verify_managed_role=False) != before:
                raise ValueError(f"Files changed after preflight: {resources}, {target}, {shared}")
            if role is not None:
                verify_role_snapshot(role, role_before)
            if role is not None and role_before is not None:
                role_recovery_directory(role, target).mkdir(mode=0o700)
            record["state"] = "prepared"
            save(folder, record)
            installation = list(parts(target, shared, folder, role))
            for kind, path, scratch, _ in installation:
                had_old = role_before is not None if kind == "role" else has_part(before, kind)
                if path.exists() != had_old or linked(path):
                    raise ValueError(f"External change to installation target: {path}")
                if had_old:
                    if kind == "role":
                        verify_role_snapshot(path, role_before)
                    else:
                        verify_part(path, before, kind, role)
                    backup = scratch / f"old-{kind}"
                    path.rename(backup)
                    if kind == "role":
                        verify_role_snapshot(backup, role_before)
            for kind, destination, _, source in installation:
                if not has_part(expected, kind):
                    continue
                if destination.exists() or linked(destination):
                    raise ValueError(f"External change to installation target: {destination}")
                source.rename(destination)
            if verified_installation(target, shared, role) != expected:
                raise ValueError(f"Unexpected version after installation: {target}, {shared}")
            if role is not None:
                verify_role_snapshot(role, None)
            record["state"] = "committed"
            save(folder, record)
        except BaseException:
            recover(target, shared, folder, role)
            raise
        recover(target, shared, folder, role)
        return "Installed" if before is None else "Updated"
