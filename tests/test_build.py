from __future__ import annotations

import importlib.util
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("build_release", ROOT / "scripts/build_release.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)

    def test_payload_and_shared_resources_match_canonical_source(self):
        output = builder.build(self.folder / "skill")
        project = ROOT / "source/project"
        expected = {p.relative_to(project).as_posix(): p.read_bytes() for p in builder.source_files(project)}
        with zipfile.ZipFile(output / "assets/repo-payload.zip") as archive:
            self.assertEqual(set(archive.namelist()), set(expected))
            for name, data in expected.items():
                self.assertEqual(archive.read(name), data)
        for directory in ("assets", "references"):
            source = project / ".agents/sdd" / directory
            for path in builder.source_files(source):
                self.assertEqual(path.read_bytes(), (output / directory / path.relative_to(source)).read_bytes())

    def test_build_is_reproducible_and_does_not_overwrite(self):
        first = builder.build(self.folder / "first")
        second = builder.build(self.folder / "second")
        contents = lambda p: {f.relative_to(p): f.read_bytes() for f in builder.source_files(p)}
        self.assertEqual(contents(first), contents(second))
        with self.assertRaises(FileExistsError):
            builder.build(first)
        with self.assertRaises(ValueError):
            builder.build(ROOT / "source/not-an-output")

    def test_generated_installer_is_idempotent_and_preserves_existing_contract(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        target.mkdir()
        index = target / "docs/index.md"
        index.parent.mkdir()
        index.write_bytes(b"# Project\nBlueprint: architecture/blueprint.md\n")
        rules = target / ".agents/governance/repository.md"
        rules.parent.mkdir(parents=True)
        rules.write_bytes(b"# Existing project rules\n")
        (target / "architecture").mkdir()
        contract = target / "architecture/blueprint.md"
        contract.write_bytes(b"# Existing architecture\n")
        command = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"), "--root", str(target), "init"]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(contract.read_bytes(), b"# Existing architecture\n")
        before = {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)}
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)})

        subprocess.run(command + ["--update-skills"], check=True, capture_output=True)
        self.assertEqual(index.read_bytes(), b"# Project\nBlueprint: architecture/blueprint.md\n")
        self.assertEqual(rules.read_bytes(), b"# Existing project rules\n")

    def test_new_install_has_only_current_skills_and_no_project_entities(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        target.mkdir()
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
             "--root", str(target), "init"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            {p.parent.name for p in (target / ".agents/skills").glob("*/SKILL.md")},
            {"sdd-doc", "sdd-imp", "sdd-test-loop", "sdd-review-loop", "sdd-commit"})
        for name in ("specs", "architecture", ".codex/config.toml", "plan.md"):
            self.assertFalse((target / name).exists(), name)
        for name in ("issue.md", "blueprint.md", "draft-pr.md", "acceptance.md", "prototype-reference.md",
                     "experiment.md", "sequence.md", "contract.md", "test-plan.md"):
            self.assertTrue((target / ".agents/sdd/assets" / name).is_file(), name)

    def test_communication_install_upgrade_and_repetition(self):
        skill = builder.build(self.folder / "skill")
        communication = (skill / "assets/communication-fragment.md").read_text(encoding="utf-8").strip()
        navigation = (skill / "assets/agents-fragment.md").read_text(encoding="utf-8").strip()
        legacy = navigation.replace("## 项目入口", communication.split("\n", 1)[1].rsplit("\n", 1)[0] + "\n\n## 项目入口")
        source = (ROOT / "source/project/.agents/sdd/references/visual-confirmation.md").read_bytes()
        for newline in ("\n", "\r\n"):
            for kind in ("new", "existing", "legacy", "misplaced", "upgrade"):
                with self.subTest(newline=repr(newline), kind=kind):
                    target = self.folder / (kind + str(len(newline)))
                    target.mkdir()
                    prefix = "# 用户约定" + newline + "保留全部正文。" + newline
                    suffix = newline + "末尾规则，无结束换行"
                    old = {
                        "new": None,
                        "existing": prefix + suffix,
                        "legacy": prefix + legacy.replace("\n", newline) + suffix,
                        "misplaced": prefix + communication.replace("\n", newline) + suffix + navigation.replace("\n", newline),
                        "upgrade": prefix + communication.replace("首要沟通原则", "旧沟通原则").replace("\n", newline) + suffix + navigation.replace("\n", newline),
                    }[kind]
                    agents = target / "AGENTS.md"
                    if old is not None:
                        agents.write_bytes(old.encode("utf-8"))
                    command = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"), "--root", str(target), "init"]
                    if kind in ("legacy", "upgrade"):
                        before = agents.read_bytes()
                        denied = subprocess.run(command, capture_output=True)
                        self.assertNotEqual(denied.returncode, 0)
                        self.assertEqual(agents.read_bytes(), before)
                        self.assertEqual(list(target.iterdir()), [agents])
                    options = ["--update-skills"] if kind in ("legacy", "upgrade") else []
                    result = subprocess.run(command + options, capture_output=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    installed = agents.read_bytes().decode("utf-8")
                    self.assertTrue(installed.startswith("<!-- agent-communication:start -->"))
                    self.assertEqual(installed.count("## 首要沟通原则"), 1)
                    self.assertEqual(installed.count("<!-- agent-communication:start -->"), 1)
                    self.assertEqual(installed.count("<!-- sdd-contract-governance:start -->"), 1)
                    if old is not None:
                        self.assertIn(prefix, installed)
                        self.assertIn(suffix, installed)
                        self.assertLess(installed.index(prefix), installed.index(suffix))
                        nav = navigation.replace("\n", newline)
                        if kind == "legacy":
                            self.assertTrue(installed.endswith(prefix + nav + suffix))
                        elif kind in ("misplaced", "upgrade"):
                            self.assertTrue(installed.endswith(prefix + suffix + nav))
                        else:
                            self.assertIn(prefix + suffix, installed)
                    self.assertEqual((target / ".agents/sdd/references/visual-confirmation.md").read_bytes(), source)
                    before = {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)}
                    for repeat in ([], ["--update-skills"], []):
                        result = subprocess.run(command + repeat, capture_output=True)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)})

    def test_conclusion_first_rule_new_install_and_previous_version_upgrade(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        target.mkdir()
        command = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"), "--root", str(target), "init"]
        def run(*args):
            return subprocess.run(command + list(args), capture_output=True)
        result = run()
        self.assertEqual(result.returncode, 0, result.stderr)
        agents = target / "AGENTS.md"
        rule = target / ".agents/sdd/references/visual-confirmation.md"
        source = (ROOT / "source/project/.agents/sdd/references/visual-confirmation.md").read_bytes()
        current = (skill / "assets/communication-fragment.md").read_text(encoding="utf-8").strip()
        self.assertTrue(agents.read_text(encoding="utf-8").startswith(current))
        self.assertIn("先给结论", current)
        self.assertIn("结论先行，分层确认", rule.read_text(encoding="utf-8"))
        self.assertEqual(rule.read_bytes(), source)
        old = """<!-- agent-communication:start -->
## 首要沟通原则：可视化对齐意图

凡需用户确认、选择、Review 或验收，先按[可视化沟通与确认规范](.agents/sdd/references/visual-confirmation.md)提供可直接查看或操作的视图，再提出明确的判断点。已确认且无实质变化的授权内工作直接执行，不重复请求确认。
<!-- agent-communication:end -->"""
        body = "# 用户正文\r\n保持这些规则。\n"
        agents.write_bytes((body + agents.read_text(encoding="utf-8").replace(current, old)).encode("utf-8"))
        rule.write_text("# 可视化沟通与确认规范\n\n每次需要用户判断时，按以下顺序执行：\n", encoding="utf-8")
        before = {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)}
        self.assertNotEqual(run().returncode, 0)
        self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)})
        result = run("--update-skills")
        self.assertEqual(result.returncode, 0, result.stderr)
        installed = agents.read_bytes().decode("utf-8")
        self.assertTrue(installed.startswith(current.replace("\n", "\r\n")))
        self.assertIn(body, installed)
        self.assertEqual(installed.count("先给结论"), 1)
        self.assertEqual(rule.read_bytes(), source)
        before = {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)}
        for args in ((), ("--update-skills",)):
            result = run(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)})

    def test_bom_preserved_at_start_on_install_and_upgrade(self):
        skill = builder.build(self.folder / "skill")
        navigation = (skill / "assets/agents-fragment.md").read_text(encoding="utf-8").strip()
        for upgrade in (False, True):
            target = self.folder / str(upgrade)
            target.mkdir()
            body = "# 原项目正文\r\n保留。\n尾部"
            original = "\ufeff" + body
            if upgrade:
                original += "\r\n" + navigation.replace("## 项目入口", "## 旧项目入口").replace("\n", "\r\n")
            agents = target / "AGENTS.md"
            agents.write_bytes(original.encode("utf-8"))
            command = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"), "--root", str(target), "init"]
            result = subprocess.run(command + (["--update-skills"] if upgrade else []), capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = agents.read_bytes()
            self.assertTrue(data.startswith(b"\xef\xbb\xbf<!-- agent-communication:start -->"))
            self.assertEqual(data.count(b"\xef\xbb\xbf"), 1)
            self.assertIn(body.encode("utf-8"), data)
            for args in ([], ["--update-skills"]):
                result = subprocess.run(command + args, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(agents.read_bytes(), data)

    def test_blocked_payload_parent_fails_before_agents_write(self):
        skill = builder.build(self.folder / "skill")
        for parent in (".agents", ".agents/sdd", ".agents/sdd/references"):
            target = self.folder / parent.replace("/", "-")
            blocker = target / parent
            blocker.parent.mkdir(parents=True)
            blocker.write_bytes(b"user-owned file")
            (target / "AGENTS.md").write_bytes(b"existing body\r\n")
            before = {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)}
            for args in ([], ["--update-skills"]):
                result = subprocess.run([sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
                                         "--root", str(target), "init", *args], capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)})

    def test_managed_block_errors_and_override_leave_project_unchanged(self):
        skill = builder.build(self.folder / "skill")
        cstart, cend = "<!-- agent-communication:start -->", "<!-- agent-communication:end -->"
        nstart, nend = "<!-- sdd-contract-governance:start -->", "<!-- sdd-contract-governance:end -->"
        malformed = [cstart, cend, cend + cstart, cstart + cend + cstart + cend,
                     nstart, nend, nstart + nend + nstart + nend,
                     cstart + nstart + nend + cend, cstart + nstart + cend + nend]
        for i, content in enumerate(malformed + ["override", "override-with-marker"]):
            for options in ([], ["--update-skills"]):
                target = self.folder / f"invalid-{i}-{len(options)}"
                target.mkdir()
                (target / "AGENTS.md").write_text(content, encoding="utf-8")
                if content.startswith("override"):
                    (target / "AGENTS.override.md").write_text(nstart if content.endswith("marker") else "custom", encoding="utf-8")
                before = {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)}
                result = subprocess.run([sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
                                         "--root", str(target), "init", *options], capture_output=True)
                self.assertNotEqual(result.returncode, 0, content)
                self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)})

    def test_old_workflow_entries_block_upgrade_before_writing(self):
        skill = builder.build(self.folder / "skill")
        entries = [".agents/skills/sdd-accept/SKILL.md"] + [
            f".codex/agents/{name}.toml" for name in
            ("sdd-requirements", "sdd-architect", "sdd-planner", "sdd-implementer", "sdd-acceptor")]
        for i, entry in enumerate(entries):
            for options in ([], ["--update-skills"]):
                with self.subTest(entry=entry, options=options):
                    target = self.folder / f"legacy-{i}-{len(options)}"
                    old = target / entry
                    old.parent.mkdir(parents=True)
                    old.write_bytes(b"customized legacy instructions\n")
                    before = {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)}
                    result = subprocess.run(
                        [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
                         "--root", str(target), "init", *options],
                        capture_output=True, text=True, encoding="utf-8")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(old.parent.name if old.name == "SKILL.md" else old.name, result.stderr)
                    self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)})

    def test_distribution_is_generic_and_reference_paths_resolve(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "unrelated-project"
        target.mkdir()
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
             "--root", str(target), "init"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        for base in (skill, target):
            for path in base.rglob("*.md"):
                text = path.read_text(encoding="utf-8")
                for marker in ("hanxue-live", "dc-contract.md", "examples/classroom", "课堂应用",
                               "本仓路径映射", "ARC-006/010/011", "docs/governance/repository.md"):
                    self.assertNotIn(marker, text, (path, marker))
        for path in (target / ".agents").rglob("*.md"):
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" not in link and not link.startswith("#"):
                    self.assertTrue((path.parent / link.split("#")[0]).is_file(), (path, link))

    def test_unknown_payload_path_rejected_before_writing(self):
        skill = builder.build(self.folder / "skill")
        with zipfile.ZipFile(skill / "assets/repo-payload.zip", "a") as archive:
            archive.writestr(".agents/sdd/references/unapproved.md", "unexpected")
        target = self.folder / "project"
        target.mkdir()
        agents = target / "AGENTS.md"
        agents.write_bytes(b"existing rules\r\n")
        result = subprocess.run([sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
                                 "--root", str(target), "init"], capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("非法路径", result.stderr)
        self.assertEqual(list(target.iterdir()), [agents])
        self.assertEqual(agents.read_bytes(), b"existing rules\r\n")

    def test_missing_new_template_rejected_before_writing(self):
        skill = builder.build(self.folder / "skill")
        spec = importlib.util.spec_from_file_location("candidate_govern", skill / "scripts/govern.py")
        installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer)
        original = installer.PROJECT_PAYLOAD
        for missing in ("assets/test-plan.md", "assets/module-design.md", "assets/sequence-flows.md", "references/document-writing.md", "references/visual-confirmation.md"):
            with self.subTest(missing=missing):
                broken = self.folder / (Path(missing).name + ".zip")
                with zipfile.ZipFile(original) as source, zipfile.ZipFile(broken, "w") as dest:
                    for name in source.namelist():
                        if name != ".agents/sdd/" + missing:
                            dest.writestr(name, source.read(name))
                installer.PROJECT_PAYLOAD = broken
                target = self.folder / Path(missing).name
                target.mkdir()
                with self.assertRaises(ValueError):
                    installer.cmd_init(target, installer.build_parser().parse_args(["init"]))
                self.assertEqual(list(target.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
