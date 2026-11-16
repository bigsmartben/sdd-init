"""Manage the user-level initializer and shared workflow resources."""
import argparse
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import sys

from .installer import (
    ROLE_LOCK, check_pending_role_recovery, install, legacy_role, load, locations,
    recover_installation, role_snapshot, verified_installation,
)
from .release import LOCK_BYTES, USER_LOCK, content_id, linked, shared_files, verify_distribution


def show_versions(label, files):
    print(f"{label} release: sha256:{content_id(files)}")
    if shared_files(files):
        print(f"{label} shared version: sha256:{content_id(shared_files(files))}")


def inspect(skills_dir: Path, resources: Path, agents_dir: Path | None = None):
    target, shared, folder = locations(skills_dir)
    role = legacy_role(target, shared, folder, agents_dir)
    print(f"User skill: {target}")
    print(f"Shared workflow: {shared}")
    if role is not None:
        print(f"Legacy user role to retire: {role}")
    print("Impact: every project linked to the shared directory uses its contents")
    candidate = None
    if (resources / "build-manifest.json").is_file():
        try:
            print(f"Distribution: sdd-init {version('sdd-init')} ({resources})")
        except PackageNotFoundError:
            print(f"Distribution: {resources}")
        candidate = verify_distribution(resources)
        show_versions("Candidate", candidate)
    if folder.exists() or linked(folder):
        print(f"Pending installation: {folder}")
        record = load(target, folder, role)
        print(f"State: {record['state'] if record else 'staging'}")
        if record and record["before"]:
            show_versions("Previous", record["before"])
        if record:
            show_versions("Intended", record["after"])
        print("Next: run sdd-init recover with the same Skill directory")
        return
    locks = [target.parent / USER_LOCK]
    if role is not None:
        locks.append(role.parent / ROLE_LOCK)
    for lock in locks:
        if linked(lock) or (lock.exists() and not lock.is_file()):
            raise ValueError(f"Invalid or linked installation lock: {lock}")
        if lock.is_file():
            with lock.open("rb") as stream:
                stream.seek(1)
                if stream.read() != LOCK_BYTES[1:]:
                    raise ValueError(f"Legacy or invalid installation lock; preserve and review backups: {lock}")
    if role is not None:
        check_pending_role_recovery(role)
        role_snapshot(role)
    files = verified_installation(target, shared, role, verify_managed_role=False)
    if files is None:
        print("Status: not installed")
        print("Next: run sdd-init install to publish the selected release")
        return
    show_versions("Installed", files)
    if candidate is not None:
        print("Status: current" if files == candidate else "Next: run sdd-init install to publish the selected release")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("install", "Install or update the user-level skill and shared workflow resources"),
        ("inspect", "Inspect the user-level installation without writing"),
        ("recover", "Recover an interrupted user-level installation"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--skills-dir", type=Path, default=Path.home() / ".agents/skills",
                             help="Skill parent directory (default: ~/.agents/skills)")
        command.add_argument("--agents-dir", type=Path,
                             help="Original user role directory for legacy installation recovery only")
    args = parser.parse_args()
    resources = Path(__file__).parent / "resources"
    try:
        if args.command == "inspect":
            inspect(args.skills_dir, resources, args.agents_dir)
        elif args.command == "recover":
            result = recover_installation(args.skills_dir, args.agents_dir)
            print("Recovered user-level installation" if result else "No pending user-level recovery")
            inspect(args.skills_dir, resources, args.agents_dir)
        else:
            previous_role = legacy_role(*locations(args.skills_dir), args.agents_dir)
            result = install(resources, args.skills_dir, args.agents_dir)
            target, shared, _ = locations(args.skills_dir)
            print(f"{result}: {target}")
            print(f"{result}: {shared}")
            if previous_role is not None:
                print(f"Retired managed user role: {previous_role}")
            inspect(args.skills_dir, resources, args.agents_dir)
            print("Select sdd-init in a target repository to connect or refresh its workflow and preset roles.")
    except (OSError, ValueError) as error:
        print(f"sdd-init: {error}", file=sys.stderr)
        return 1
    return 0
