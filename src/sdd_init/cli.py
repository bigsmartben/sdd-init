"""Initialize the user-level sdd-init skill and configure a target repository."""
import argparse
import os
from pathlib import Path
import stat
import sys
import tempfile

from . import repository


def apply(resources: Path, home: Path, install: bool) -> int:
    home = home.absolute()
    if not (resources / "SKILL.md").is_file():
        raise ValueError("Package resources missing. Install from a built distribution.")
    pending = []
    conflicts = []
    for path in (home, *home.parents):
        try:
            metadata = path.lstat()
        except (FileNotFoundError, NotADirectoryError):
            continue
        junction = os.name == "nt" and metadata.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT
        if stat.S_ISLNK(metadata.st_mode) or junction:
            raise ValueError(f"Linked skill directory: {path}")
    home = home.resolve()
    for source in sorted(resources.rglob("*")):
        if not source.is_file():
            continue
        target = home / source.relative_to(resources)
        if (target.resolve() != target or target.is_symlink()
                or any(parent.exists() and not parent.is_dir() for parent in target.parents)):
            conflicts.append(target)
        elif target.is_file() and target.read_bytes() == source.read_bytes():
            continue
        elif target.exists():
            conflicts.append(target)
        else:
            pending.append((source, target))
    if conflicts:
        for path in conflicts:
            print(f"Conflicting file: {path}", file=sys.stderr)
        return 1
    for source, target in pending:
        print(f"{'Installing' if install else 'Missing'}: {target}")
        if install:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
                temporary = Path(stream.name)
            try:
                temporary.write_bytes(source.read_bytes())
                try:
                    os.link(temporary, target)
                except FileExistsError:
                    if target.is_symlink() or target.read_bytes() != source.read_bytes():
                        raise
            finally:
                temporary.unlink()
    if install or not pending:
        print("Status: current")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("install", "inspect"):
        command = commands.add_parser(name)
        location = command.add_mutually_exclusive_group()
        location.add_argument("--home", type=Path, default=Path.home(),
                              help="Parent of .agents (defaults to your home directory)")
        location.add_argument("--skills-dir", type=Path, help="Explicit parent directory for sdd-init")
    repository.add_arguments(commands.add_parser("project"))
    args = parser.parse_args()
    try:
        resources = Path(__file__).with_name("resources")
        if args.command == "project":
            return repository.run(resources / "assets", args)
        directory = args.skills_dir if args.skills_dir is not None else args.home / ".agents/skills"
        target = (directory / "sdd-init").absolute()
        print(f"User skill: {target}")
        return apply(resources, target, args.command == "install")
    except (OSError, ValueError) as error:
        print(f"sdd-init: {error}", file=sys.stderr)
        return 1
