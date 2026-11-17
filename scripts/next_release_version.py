"""Select the next release version and update project metadata."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import tomllib


VERSION = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")
VERSION_LINE = re.compile(r'(?m)^version\s*=\s*"([^"\r\n]+)"\s*$')


def version_tuple(value: str) -> tuple[int, int, int]:
    match = VERSION.fullmatch(value)
    if not match:
        raise ValueError(f"Expected a stable major.minor.patch version, got {value!r}")
    return tuple(int(part) for part in match.groups())


def update_version(base_text: str, candidate_text: str) -> tuple[str, str]:
    base = version_tuple(tomllib.loads(base_text)["project"]["version"])
    candidate_value = tomllib.loads(candidate_text)["project"]["version"]
    candidate = version_tuple(candidate_value)
    matches = list(VERSION_LINE.finditer(candidate_text))
    if len(matches) != 1 or matches[0].group(1) != candidate_value:
        raise ValueError("Expected one project version line in candidate metadata")
    chosen = candidate if candidate > base else (base[0], base[1], base[2] + 1)
    version = ".".join(str(part) for part in chosen)
    start, end = matches[0].span(1)
    return version, candidate_text[:start] + version + candidate_text[end:]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--project", type=Path, default=Path("pyproject.toml"))
    args = parser.parse_args()
    with args.base.open(encoding="utf-8", newline="") as source:
        base_text = source.read()
    with args.project.open(encoding="utf-8", newline="") as source:
        candidate_text = source.read()
    version, updated = update_version(base_text, candidate_text)
    if updated != candidate_text:
        with args.project.open("w", encoding="utf-8", newline="") as target:
            target.write(updated)
    print(version)


if __name__ == "__main__":
    main()
