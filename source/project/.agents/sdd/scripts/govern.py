#!/usr/bin/env python3
"""Read-only project inventory. Use current Skills for project work."""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import sys

def out(message: str) -> None:
    print(message)


def fail(message: str) -> None:
    raise ValueError(message)


def require_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        fail(f"仓库目录不存在: {root}")
    return root


def git(root: Path, *args: str) -> bytes | None:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=False)
        return r.stdout if r.returncode == 0 else None
    except FileNotFoundError:
        return None


def cmd_inspect(root: Path, _: argparse.Namespace) -> int:
    out(f"Repository: {root}")
    for rel in ["AGENTS.md", "docs/index.md", "docs/blueprint.md", "specs"]:
        out(f"{'EXISTS' if (root / rel).exists() else 'MISSING'}  {rel}")
    specs = sorted((root / "specs").glob("*/spec.md")) if (root / "specs").exists() else []
    for spec in specs:
        status = spec.with_name("status.md")
        out(f"CAPABILITY {spec.parent.name}: spec=present status={'present' if status.exists() else 'missing'}")
    candidates = [p for p in (root / "docs").rglob("*.md") if any(x in p.name.lower() for x in ("architecture", "design", "blueprint"))] if (root / "docs").is_dir() else []
    for p in candidates[:20]:
        out(f"POSSIBLE_EXISTING_ARCH {p.relative_to(root)} (请人工判断，禁止自动替换)")
    out(f"Git HEAD: {(git(root, 'rev-parse', '--short', 'HEAD') or b'none').decode().strip()}")
    out("这是只读盘点；安装与升级按实际任务授权执行。")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_subparsers(dest="cmd", required=True).add_parser("inspect")
    args = parser.parse_args(argv)
    try:
        return cmd_inspect(require_root(args.root), args)
    except (ValueError, OSError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
