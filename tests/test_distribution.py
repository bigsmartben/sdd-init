import importlib.util
from pathlib import Path
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sdd_init.cli import apply

spec = importlib.util.spec_from_file_location("builder", ROOT / "scripts/build_release.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class DistributionTests(unittest.TestCase):
    def test_legacy_task_label_resolves_to_shipped_role(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = builder.build(Path(directory) / "bundle")
            main = (bundle / ".codex/AGENTS.md").read_text("utf-8")
            self.assertRegex(main, r"\[Coder\][^。\n]*implementer")
            roles = bundle / ".codex/agents"
            self.assertFalse((roles / "coder.toml").exists())
            role = tomllib.loads((roles / "implementer.toml").read_text("utf-8"))
            self.assertEqual(role["name"], "implementer")

    def test_published_main_lists_scene_aliases_and_chain_endpoints(self):
        aliases = {
            "arch／架构", "blueprint／蓝图", "plan／计划／实施方案", "diagnose／诊断／排查",
            "implent／实现／修复", "verify／测试／质量评估", "build／构建／CI", "live-uat／陪测／人工验收",
        }
        with tempfile.TemporaryDirectory() as directory:
            bundle = builder.build(Path(directory) / "bundle")
            main = (bundle / ".codex/AGENTS.md").read_text("utf-8")
            rows = {line.split("|")[1].strip() for line in main.splitlines()
                    if line.startswith("|") and "／" in line.split("|")[1]}
            self.assertEqual(rows, aliases)
            for chain in ("【blueprint->plan】", "【blueprint->implent】"):
                self.assertIn(chain, main)

    def test_quality_outcomes_are_understood_by_main(self):
        source = ROOT / "source/project/.codex"
        main = (source / "AGENTS.md").read_text("utf-8")
        tester = tomllib.loads((source / "agents/tester.toml").read_text("utf-8"))
        for outcome in ("REJECTED", "PASS", "FAIL", "NEEDS_DECISION", "BLOCKED"):
            with self.subTest(outcome=outcome):
                self.assertIn(outcome, tester["developer_instructions"])
                self.assertIn(outcome, main)

    def test_conflict_preflight_and_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = builder.build(root / "bundle")
            home = root / "home"
            main = home / ".codex/AGENTS.md"
            main.parent.mkdir(parents=True)
            main.write_bytes(b"personal")
            self.assertEqual(apply(bundle, home, True), 1)
            self.assertEqual(main.read_bytes(), b"personal")
            self.assertFalse((home / ".agents").exists())
            main.unlink()
            self.assertEqual(apply(bundle, home, False), 0)
            self.assertFalse(main.exists())
            self.assertEqual(apply(bundle, home, True), 0)
            self.assertEqual(apply(bundle, home, True), 0)
            for name in builder.FILES:
                self.assertEqual((home / name).read_bytes(), (bundle / name).read_bytes())
