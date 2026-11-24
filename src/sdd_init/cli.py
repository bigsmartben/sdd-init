"""Install or inspect Main and its six vertical agents."""
import argparse
import os
from pathlib import Path
import sys
import tempfile


def apply(resources: Path, home: Path, install: bool) -> int:
    if not resources.is_dir():
        raise ValueError("Package resources missing. Install from a built distribution.")
    pending = []
    conflicts = []
    for source in sorted(resources.rglob("*")):
        if not source.is_file():
            continue
        target = home / source.relative_to(resources)
        if target.is_symlink() or not target.resolve().is_relative_to(home.resolve()):
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
    parser.add_argument("command", choices=("install", "inspect"))
    parser.add_argument("--home", type=Path, default=Path.home(),
                        help="Parent of .codex (defaults to your home directory)")
    args = parser.parse_args()
    try:
        return apply(Path(__file__).with_name("resources"), args.home.resolve(), args.command == "install")
    except (OSError, ValueError) as error:
        print(f"sdd-init: {error}", file=sys.stderr)
        return 1
