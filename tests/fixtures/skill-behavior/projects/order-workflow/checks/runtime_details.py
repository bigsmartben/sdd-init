"""Read-only runtime facts; this output is not an acceptance result."""
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
print(json.dumps({
    "python": sys.version,
    "sqlite": sqlite3.sqlite_version,
    "runtime": json.loads((ROOT / "runtime.json").read_text(encoding="utf-8")),
    "source_sha256": {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted((ROOT / "src").glob("*.py"))},
}, ensure_ascii=False, indent=2))
