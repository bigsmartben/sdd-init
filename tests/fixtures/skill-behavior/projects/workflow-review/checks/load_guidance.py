"""Read the two instruction layers without executing a model."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for name in ("main", "prompt"):
    print((root / f"guidance/{name}.md").read_text(encoding="utf-8"))
