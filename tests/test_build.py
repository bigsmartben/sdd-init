from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

WORKFLOW = ".agents/skills/sdd-workflow"
ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("build_release", ROOT / "scripts/build_release.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def project_entries(root):
    """Installation may create only its stable one-byte lock during preflight."""
    lock = root / ".sdd-init.lock"
    if lock.exists():
        assert lock.read_bytes() == b"\0", lock
    return [p for p in root.iterdir() if p != lock]


def project_files(root):
    project_entries(root)
    return [p for p in root.rglob("*") if p.is_file() and p != root / ".sdd-init.lock"
            and not p.is_relative_to(root / WORKFLOW)]


def refresh_manifest(build):
    manifest = build / "build-manifest.json"
    files = {path.relative_to(build).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in builder.source_files(build) if path != manifest}
    manifest.write_text(json.dumps({"schema_version": 1, "files": files}), encoding="utf-8")


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)

    def test_payload_and_shared_resources_match_canonical_source(self):
        output = builder.build(self.folder / "skill")
        project = ROOT / "source/project"
        for source, target in ((".agents/skills", "skills"), (".agents/sdd", "sdd"),
                               (".codex/agents", "agents")):
            canonical = project / source
            shared = output / "shared" / target
            expected = {p.relative_to(canonical): p.read_bytes() for p in builder.source_files(canonical)}
            self.assertEqual({p.relative_to(shared): p.read_bytes() for p in builder.source_files(shared)}, expected)
        self.assertFalse((output / "assets/repo-payload.zip").exists())
        self.assertFalse((output / "assets/spec_template.md").exists())

    def test_build_is_reproducible_and_does_not_overwrite(self):
        first = builder.build(self.folder / "first")
        second = builder.build(self.folder / "second")
        contents = lambda p: {f.relative_to(p): f.read_bytes() for f in builder.source_files(p)}
        self.assertEqual(contents(first), contents(second))
        with self.assertRaises(FileExistsError):
            builder.build(first)
        with self.assertRaises(ValueError):
            builder.build(ROOT / "source/not-an-output")

    def test_init_connects_cleaned_project_and_preserves_project_configuration(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        target.mkdir()
        index = target / "docs/index.md"
        index.parent.mkdir()
        index_body = b"# Project\n[Previous template](../.agents/sdd/assets/spec_template.md)\n"
        index.write_bytes(index_body)
        rules = target / "docs/repository-governance.md"
        rules.write_bytes(b"# Existing project rules\n")
        agents = target / "AGENTS.md"
        project_rules = b"# Existing project guidance\r\n"
        agents.write_bytes(project_rules + (
            b"\r\n<!-- sdd-contract-governance:start -->\r\n"
            b"[Previous governance](.agents/sdd/references/sdd-repository-governance.md)\r\n"
            b"<!-- sdd-contract-governance:end -->\r\n"
        ))
        config = target / ".codex/config.toml"
        config.parent.mkdir()
        project_config = b'model = "main-model"\r\n[mcp_servers.custom]\r\nurl = "https://example.invalid/mcp"\r\n'
        config.write_bytes(project_config + (
            b"\r\n# sdd-init roles:start\r\n[agents.sdd-coder]\r\n"
            b'config_file = "agents/sdd-coder.toml"\r\n'
            b"# sdd-init roles:end\r\n"
        ))
        (target / "architecture").mkdir()
        contract = target / "architecture/blueprint.md"
        contract.write_bytes(b"# Existing architecture\n")
        command = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"), "--root", str(target), "init"]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(contract.read_bytes(), b"# Existing architecture\n")
        self.assertIn(project_rules, agents.read_bytes())
        self.assertIn(WORKFLOW.encode(), agents.read_bytes())
        self.assertNotIn(b"Previous governance", agents.read_bytes())
        self.assertTrue(config.read_bytes().startswith(project_config))
        self.assertIn(f'config_file = "../{WORKFLOW}/agents/sdd-coder.toml"'.encode(), config.read_bytes())
        self.assertTrue((target / WORKFLOW).samefile(skill / "shared"))
        self.assertEqual(index.read_bytes(), index_body)
        self.assertEqual(rules.read_bytes(), b"# Existing project rules\n")
        before = {p.relative_to(target): p.read_bytes() for p in project_files(target)}
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in project_files(target)})

    def test_new_install_has_only_current_skills_and_no_project_entities(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        target.mkdir()
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
             "--root", str(target), "init"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            {p.parent.name for p in (target / WORKFLOW / "skills").glob("*/SKILL.md")},
            {"sdd-develop", "sdd-bugfix", "sdd-test-loop", "sdd-review-code",
             "sdd-review-prompt", "sdd-deliver"})
        for name in ("specs", "architecture", ".codex/agents", ".agents/sdd", "plan.md", "docs/index.md", "docs/code-review-rules.md"):
            self.assertFalse((target / name).exists(), name)
        for name in ("spec_template.md", "blueprint_template.md", "plan_template.md", "quickstart_template.md", "prototype_reference_template.md",
                     "test_report_template.md", "issue_template.md", "review_template.md", "sequence_template.md", "contract_template.md"):
            self.assertTrue((target / WORKFLOW / "sdd/assets" / name).is_file(), name)
        assets = target / WORKFLOW / "sdd/assets"
        self.assertEqual(
            {p.name for p in assets.glob("*.md")},
            {"spec_template.md", "blueprint_template.md", "status_template.md",
             "plan_template.md", "quickstart_template.md", "prototype_reference_template.md",
             "test_report_template.md", "issue_template.md", "review_template.md", "sequence_template.md", "contract_template.md",
             "architecture-rule-catalog.md", "code-review-rules_template.md", "research_template.md"})
        checker = target / WORKFLOW / "sdd/scripts/doc_check.py"
        checked = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(checker), "--root", str(target),
             "--format", "json", "AGENTS.md"],
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertFalse((target / WORKFLOW / "sdd/assets/issue.md").exists())
        for retired in ("draft-pr.md", "test-plan.md", "acceptance.md", "module-design.md"):
            self.assertFalse((target / WORKFLOW / "sdd/assets" / retired).exists(), retired)

    def test_project_code_review_rules_survive_install_and_upgrade(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        rules = target / "docs/code-review-rules.md"
        rules.parent.mkdir(parents=True)
        content = "# Code Review Rules\n\nCR-001 用户确认的项目规则。\n".encode("utf-8")
        rules.write_bytes(content)
        command = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
                   "--root", str(target), "init"]
        for _ in range(2):
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(rules.read_bytes(), content)
            self.assertTrue((target / WORKFLOW / "sdd/assets/code-review-rules_template.md").is_file())

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
                    result = subprocess.run(command, capture_output=True)
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
                    self.assertEqual((target / WORKFLOW / "sdd/references/visual-confirmation.md").read_bytes(), source)
                    before = {p.relative_to(target): p.read_bytes() for p in project_files(target)}
                    result = subprocess.run(command, capture_output=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in project_files(target)})

    def test_confirmation_trigger_new_install_and_previous_version_upgrade(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        target.mkdir()
        command = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"), "--root", str(target), "init"]
        def run():
            return subprocess.run(command, capture_output=True)
        result = run()
        self.assertEqual(result.returncode, 0, result.stderr)
        agents = target / "AGENTS.md"
        rule = target / WORKFLOW / "sdd/references/visual-confirmation.md"
        source = (ROOT / "source/project/.agents/sdd/references/visual-confirmation.md").read_bytes()
        current = (skill / "assets/communication-fragment.md").read_text(encoding="utf-8").strip()
        self.assertTrue(agents.read_text(encoding="utf-8").startswith(current))
        confirmation_link = f"[意图对齐]({WORKFLOW}/sdd/references/visual-confirmation.md#意图对齐)"
        self.assertIn("必须呈现对用户意图的理解并请求确认，不以推断代替确认；已有确认沿用，新增或变化内容重新对齐。", current)
        self.assertIn(confirmation_link, current)
        self.assertIn("需求与方案分开讨论、分别确认", rule.read_text(encoding="utf-8"))
        self.assertEqual(rule.read_bytes(), source)
        old = """<!-- agent-communication:start -->
## 首要沟通原则：可视化对齐意图

凡需用户确认、选择、Review 或验收，先按[可视化沟通与确认规范](.agents/sdd/references/visual-confirmation.md)提供可直接查看或操作的视图，再提出明确的判断点。已确认且无实质变化的授权内工作直接执行，不重复请求确认。
<!-- agent-communication:end -->"""
        body = "# 用户正文\r\n保持这些规则。\n"
        agents.write_bytes((body + agents.read_text(encoding="utf-8").replace(current, old)).encode("utf-8"))
        result = run()
        self.assertEqual(result.returncode, 0, result.stderr)
        installed = agents.read_bytes().decode("utf-8")
        self.assertTrue(installed.startswith(current.replace("\n", "\r\n")))
        self.assertIn(body, installed)
        self.assertEqual(installed.count(confirmation_link), 1)
        self.assertEqual(rule.read_bytes(), source)
        before = {p.relative_to(target): p.read_bytes() for p in project_files(target)}
        result = run()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in project_files(target)})

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
            result = subprocess.run(command, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = agents.read_bytes()
            self.assertTrue(data.startswith(b"\xef\xbb\xbf<!-- agent-communication:start -->"))
            self.assertEqual(data.count(b"\xef\xbb\xbf"), 1)
            self.assertIn(body.encode("utf-8"), data)
            result = subprocess.run(command, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(agents.read_bytes(), data)

    def test_blocked_payload_parent_fails_before_agents_write(self):
        skill = builder.build(self.folder / "skill")
        for parent in (".agents", ".agents/skills", WORKFLOW):
            target = self.folder / parent.replace("/", "-")
            blocker = target / parent
            blocker.parent.mkdir(parents=True)
            blocker.write_bytes(b"user-owned file")
            (target / "AGENTS.md").write_bytes(b"existing body\r\n")
            before = {p.relative_to(target): p.read_bytes() for p in project_files(target)}
            result = subprocess.run([sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
                                     "--root", str(target), "init"], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in project_files(target)})

    def test_managed_block_errors_and_override_leave_project_unchanged(self):
        skill = builder.build(self.folder / "skill")
        cstart, cend = "<!-- agent-communication:start -->", "<!-- agent-communication:end -->"
        nstart, nend = "<!-- sdd-contract-governance:start -->", "<!-- sdd-contract-governance:end -->"
        malformed = [cstart, cend, cend + cstart, cstart + cend + cstart + cend,
                     nstart, nend, nstart + nend + nstart + nend,
                     cstart + nstart + nend + cend, cstart + nstart + cend + nend]
        for i, content in enumerate(malformed + ["override", "override-with-marker"]):
            target = self.folder / f"invalid-{i}"
            target.mkdir()
            (target / "AGENTS.md").write_text(content, encoding="utf-8")
            if content.startswith("override"):
                (target / "AGENTS.override.md").write_text(nstart if content.endswith("marker") else "custom", encoding="utf-8")
            before = {p.relative_to(target): p.read_bytes() for p in project_files(target)}
            result = subprocess.run([sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
                                     "--root", str(target), "init"], capture_output=True)
            self.assertNotEqual(result.returncode, 0, content)
            self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in project_files(target)})

    def test_init_leaves_files_outside_the_current_workflow_scope(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        files = {
            ".agents/sdd/assets/test-plan.md": b"# Project notes\n",
            ".agents/skills/sdd-accept/SKILL.md": b"# Existing workflow notes\n",
            ".codex/agents/sdd-architect.toml": b'name = "sdd-architect"\n',
        }
        for relative, content in files.items():
            entry = target / relative
            entry.parent.mkdir(parents=True, exist_ok=True)
            entry.write_bytes(content)
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
             "--root", str(target), "init"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        for relative, content in files.items():
            self.assertEqual((target / relative).read_bytes(), content)

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
        for path in (target / WORKFLOW).rglob("*.md"):
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" not in link and not link.startswith("#"):
                    self.assertTrue((path.parent / link.split("#")[0]).is_file(), (path, link))

    def test_unregistered_shared_file_rejected_before_writing(self):
        skill = builder.build(self.folder / "skill")
        extra = skill / "shared/sdd/references/unapproved.md"
        extra.write_text("unexpected", encoding="utf-8")
        target = self.folder / "project"
        target.mkdir()
        agents = target / "AGENTS.md"
        agents.write_bytes(b"existing rules")
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
             "--root", str(target), "init"], capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("清单不一致", result.stderr)
        self.assertEqual(project_entries(target), [agents])
        self.assertEqual(agents.read_bytes(), b"existing rules")

    def test_missing_required_shared_resources_fail_before_writing(self):
        skill = builder.build(self.folder / "skill")
        for index, relative in enumerate((
            "skills/sdd-deliver/SKILL.md", "skills/sdd-deliver/agents/openai.yaml",
            "skills/sdd-deliver/references/git-delivery.md", "skills/sdd-deliver/references/git-remote.md",
            "skills/sdd-deliver/references/deployment.md",
            "skills/sdd-review-prompt/SKILL.md", "skills/sdd-review-prompt/agents/openai.yaml",
            "skills/sdd-bugfix/SKILL.md", "skills/sdd-bugfix/agents/openai.yaml",
            "skills/sdd-develop/SKILL.md", "skills/sdd-develop/agents/openai.yaml",
            "sdd/references/implementation.md",
            "sdd/scripts/govern.py", "sdd/scripts/doc_check.py", "sdd/references/doc-check.md",
            "sdd/assets/status_template.md", "sdd/assets/code-review-rules_template.md",
            "sdd/assets/spec_template.md", "sdd/assets/quickstart_template.md",
            "sdd/assets/plan_template.md", "sdd/assets/sequence_template.md",
            "sdd/assets/test_report_template.md", "sdd/assets/issue_template.md",
            "sdd/assets/review_template.md", "sdd/assets/research_template.md", "sdd/references/document-writing.md",
            "sdd/references/visual-confirmation.md",
        )):
            with self.subTest(missing=relative):
                path = skill / "shared" / relative
                original = path.read_bytes()
                path.unlink()
                refresh_manifest(skill)
                target = self.folder / f"missing-{index}"
                target.mkdir()
                result = subprocess.run(
                    [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
                     "--root", str(target), "init"], capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(project_entries(target), [])
                path.write_bytes(original)
                refresh_manifest(skill)


if __name__ == "__main__":
    unittest.main()
