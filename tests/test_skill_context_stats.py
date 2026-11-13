import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("stats", ROOT / "scripts/skill_context_stats.py")
stats = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stats)


class ContextStatsTests(unittest.TestCase):
    def test_unicode_anchor_dedup_missing_and_read_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            entry = root / "SKILL.md"
            entry.write_text("---\ndescription: 中文\n---\n[a](ref.md#a) [b](ref.md#b) [x](missing.md) [web](https://example.com)\n", encoding="utf-8")
            (root / "ref.md").write_text("中文abc", encoding="utf-8")
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            result = stats.measure(entry, root)
            self.assertEqual(result["description_characters"], 2)
            self.assertEqual(result["entry_characters"], len(entry.read_text(encoding="utf-8")))
            self.assertEqual(result["direct_references"], {
                "ref.md": {"characters": 5, "missing": False},
                "missing.md": {"characters": None, "missing": True},
            })
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})

    def test_projected_initializer_references_resolve(self):
        result = stats.report(ROOT)
        self.assertEqual(len(result["skills"]), 9)
        for skill in result["skills"]:
            self.assertTrue(all(not ref["missing"] for ref in skill["direct_references"].values()), skill)
