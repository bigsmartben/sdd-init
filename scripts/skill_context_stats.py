"""Read-only character counts; reference sizes are not invocation costs or tokens."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def measure(entry: Path, root: Path) -> dict:
    content = entry.read_text(encoding="utf-8")
    description = re.search(r"^description:\s*(.*)$", content, re.MULTILINE)
    references = {}
    for link in re.findall(r"\]\(([^)]+)\)", content):
        parsed = urlsplit(link)
        if parsed.scheme or not parsed.path:
            continue
        target = (entry.parent / unquote(parsed.path)).resolve()
        # Initializer references are projected from shared sources by the builder.
        if not target.exists() and entry == root / "source/initializer/SKILL.md":
            target = root / "source/project/.agents/sdd" / unquote(parsed.path)
        key = target.relative_to(root).as_posix()
        if key not in references:
            references[key] = {
                "characters": len(target.read_text(encoding="utf-8")) if target.is_file() else None,
                "missing": not target.is_file(),
            }
    return {
        "entry": entry.relative_to(root).as_posix(),
        "entry_characters": len(content),
        "description_characters": len(description.group(1)) if description else 0,
        "direct_references": references,
    }


def report(root: Path) -> dict:
    root = root.resolve()
    entries = [root / "source/initializer/SKILL.md"]
    entries += sorted((root / "source/project/.agents/skills").glob("*/SKILL.md"))
    return {
        "unit": "Unicode characters, not tokens",
        "note": "Entry includes description. References count whole files once per entry; conditional reads and anchors may read less. No recursive or actual invocation cost is inferred.",
        "skills": [measure(entry, root) for entry in entries],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(report(args.root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
