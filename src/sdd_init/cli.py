"""Console entry point; project initialization remains the skill's responsibility."""
import argparse
from pathlib import Path
import sys

from .installer import install, shared_directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("install", help="Install or update the user-level skill")
    command.add_argument("--skills-dir", type=Path, default=Path.home() / ".agents/skills",
                         help="Skill parent directory (default: ~/.agents/skills)")
    args = parser.parse_args()
    try:
        result = install(Path(__file__).parent / "resources", args.skills_dir)
    except (OSError, ValueError) as error:
        print(f"sdd-init: {error}", file=sys.stderr)
        return 1
    print(f"{result}: {args.skills_dir / 'sdd-init'}")
    print(f"Shared workflow: {shared_directory(args.skills_dir.expanduser().absolute())}")
    print("Open your target repository in Codex and select sdd-init to connect it.")
    return 0
