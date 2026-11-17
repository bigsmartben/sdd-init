"""Flat skill discovery and restartable link migration, entirely in temporary paths."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


builder = module(ROOT / "scripts/build_release.py", "flat_link_builder")


class FlatSkillLinkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name).resolve()
        self.root = self.home / "project"
        self.root.mkdir()
        self.skill = builder.build(self.home / "initializer")
        self.gov = module(self.skill / "scripts/govern.py", "flat_link_govern")
        self.tx = self.gov.transaction
        self.shared = self.skill / "shared"
        self.args = self.gov.build_parser().parse_args(["init"])
        self.legacy_fragments = {}
        assets = self.skill / "assets"
        for name, filename in self.gov.FRAGMENTS.items():
            text = (assets / filename).read_text(encoding="utf-8").strip()
            old = text.replace(self.tx.WORKFLOW_LINK + "/", self.tx.LEGACY_WORKFLOW_LINK + "/")
            for skill in self.gov.PROJECT_SKILLS:
                old = old.replace(f".agents/skills/{skill}/", f"{self.tx.LEGACY_WORKFLOW_LINK}/skills/{skill}/")
            self.legacy_fragments[name] = old
        self.shared_before = self.shared_files()

    def refresh_manifest(self):
        path = self.skill / "build-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["files"] = {relative: self.gov.release.digest((self.skill / relative).read_bytes())
                             for relative in manifest["files"]}
        path.write_text(json.dumps(manifest), encoding="utf-8")

    def shared_files(self):
        return {p.relative_to(self.shared).as_posix(): p.read_bytes()
                for p in self.shared.rglob("*") if p.is_file() and p.suffix != ".pyc"}

    def snapshot(self):
        """Do not traverse any link, including junctions on Python 3.11."""
        result, pending = {}, [self.root]
        while pending:
            for path in pending.pop().iterdir():
                if path.name == self.tx.LOCK:
                    continue
                relative = path.relative_to(self.root).as_posix()
                if self.tx.linked(path):
                    result[relative] = ("link", str(self.tx.workflow_target(path)))
                elif path.is_dir():
                    pending.append(path)
                else:
                    result[relative] = path.read_bytes()
        return result

    def init(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return self.gov.cmd_init(self.root, self.args)

    def recover(self):
        with contextlib.redirect_stdout(io.StringIO()), self.tx.project_lock(self.root):
            return self.tx.recover(self.root)

    def assert_layout(self):
        skills = self.root / ".agents/skills"
        self.assertEqual({p.name for p in skills.iterdir()}, self.gov.PROJECT_SKILLS)
        for name in self.gov.PROJECT_SKILLS:
            path = skills / name
            self.assertTrue(self.tx.linked(path), path)
            self.assertTrue(path.is_dir(), path)
            self.assertTrue((path / "SKILL.md").samefile(self.shared / "skills" / name / "SKILL.md"))
            if os.name == "nt":
                self.assertEqual(path.lstat().st_reparse_tag, 0xA0000003)
            else:
                self.assertTrue(path.is_symlink())
        self.assertTrue((self.root / self.tx.WORKFLOW_LINK).samefile(self.shared))
        self.assertFalse(self.tx.linked(self.root / self.tx.LEGACY_WORKFLOW_LINK))

    def legacy(self, *, state=True, retired=False):
        path = self.tx.link_path(self.root, self.tx.LEGACY_WORKFLOW_LINK)
        self.tx.create_workflow_link(path, self.shared)
        agents = "Project-owned introduction\r\n\r\n" + "\r\n\r\n".join(
            fragment.replace("\n", "\r\n") for fragment in self.legacy_fragments.values()) + "\r\n"
        (self.root / "AGENTS.md").write_bytes(agents.encode())
        names = sorted(self.gov.PROJECT_ROLES | (self.gov.RETIRED_ROLES if retired else set()))
        config = 'model = "project-choice"\r\n# sdd-init roles:start\r\n' + "".join(
            f'[agents.{name}]\r\nconfig_file = "{self.gov.legacy_role_reference(name)}"\r\n'
            for name in names) + "# sdd-init roles:end\r\n"
        (self.root / ".codex").mkdir()
        (self.root / ".codex/config.toml").write_bytes(config.encode())
        (self.root / ".gitignore").write_bytes(f"/build/\r\n/{self.tx.LEGACY_WORKFLOW_LINK}\r\n".encode())
        if state:
            metadata = {"schema_version": 1, "shared_version": "0" * 64,
                        "agents_blocks": {name: self.gov.release.digest(text.encode())
                                          for name, text in self.legacy_fragments.items()}}
            (self.root / self.tx.STATE).write_text(json.dumps(metadata), encoding="utf-8")
        return path

    def crash(self, hook, *, command="init"):
        program = '''
import importlib.util, os, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("flat_link_crash", sys.argv[1])
gov = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gov)
tx = gov.transaction
root = Path(sys.argv[2])
''' + hook + f'''
gov.cmd_{command}(root, gov.build_parser().parse_args(["{command}"]))
'''
        result = subprocess.run([sys.executable, "-B", "-X", "utf8", "-c", program,
                                 str(self.skill / "scripts/govern.py"), str(self.root)],
                                capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 79, result.stderr.decode("utf-8", errors="replace"))

    def crash_after_publications(self, count=3):
        self.crash('''
original = tx.publish_workflow_link
count = 0
def stop(source, destination):
    global count
    original(source, destination)
    count += 1
    if count == ''' + str(count) + ''': os._exit(79)
tx.publish_workflow_link = stop
''')

    def test_six_flat_real_directory_links_and_anchor(self):
        self.assertEqual(self.init(), 0)
        self.assert_layout()
        self.assertEqual(self.shared_files(), self.shared_before)
        self.assertFalse((self.root / ".codex/agents").exists())
        for name in self.gov.PROJECT_ROLES:
            reference = self.root / ".codex" / self.gov.role_reference(name)
            self.assertTrue(reference.samefile(self.shared / "roles/codex" / f"{name}.toml"))

    def test_shared_updates_are_visible_without_copy_or_relink(self):
        self.init()
        name = "sdd-bugfix"
        path = self.shared / "skills" / name / "SKILL.md"
        link = self.root / ".agents/skills" / name
        identity = self.tx.link_snapshot(link)
        path.write_bytes(path.read_bytes() + b"\nShared update\n")
        self.assertTrue((link / "SKILL.md").read_bytes().endswith(b"Shared update\n"))
        self.refresh_manifest()
        self.init()
        self.assertEqual(self.tx.link_snapshot(link), identity)
        self.assert_layout()

    def test_repeat_keeps_bytes_and_link_identities(self):
        self.init()
        before = self.snapshot()
        links = self.tx.plan_links(self.root, self.shared)
        self.init()
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.tx.plan_links(self.root, self.shared), links)
        self.assertFalse((self.root / self.tx.RECOVERY).exists())

    def test_ignore_covers_each_link_after_negations(self):
        original = "# keep\n/.agents/skills/sdd-bugfix\n!.agents/**\n"
        (self.root / ".gitignore").write_text(original, encoding="utf-8")
        self.init()
        result = (self.root / ".gitignore").read_text(encoding="utf-8")
        self.assertTrue(result.startswith(original))
        for relative in (self.tx.WORKFLOW_LINK, *self.tx.SKILL_LINKS):
            self.assertIn(f"/{relative}", result.split("!.agents/**\n", 1)[1].splitlines())

    def test_inspect_reports_missing_flat_link_without_writes(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.gov.cmd_inspect(self.root, self.args)
        self.assertIn(".agents/skills/sdd-bugfix -> (missing)", output.getvalue())
        self.assertEqual(list(self.root.iterdir()), [])
        self.init()
        path = self.root / ".agents/skills/sdd-bugfix"
        self.tx.remove_workflow_link(path)
        before = self.snapshot()
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.gov.cmd_inspect(self.root, self.args)
        self.assertIn("Project changes on init: .agents/skills/sdd-bugfix", output.getvalue())
        self.assertEqual(self.snapshot(), before)

    def test_inspect_reports_existing_non_link_as_replacement(self):
        path = self.tx.link_path(self.root, self.tx.WORKFLOW_LINK)
        path.parent.mkdir(parents=True)
        path.write_bytes(b"existing entry")
        before = self.snapshot()
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.gov.cmd_inspect(self.root, self.args)
        self.assertIn("(existing file or directory)", output.getvalue())
        self.assertIn(self.tx.WORKFLOW_LINK, output.getvalue())
        self.assertEqual(self.snapshot(), before)
        self.init()
        self.assert_layout()

    def test_old_layout_with_owned_main_block_and_retired_roles_migrates(self):
        self.legacy(retired=True)
        self.init()
        self.assert_layout()
        self.assertTrue((self.root / "AGENTS.md").read_bytes().endswith(b"\r\n"))
        self.assertIn(b"Project-owned introduction", (self.root / "AGENTS.md").read_bytes())
        config = (self.root / ".codex/config.toml").read_bytes()
        self.assertTrue(config.startswith(b'model = "project-choice"\r\n'))
        self.assertNotIn(self.tx.LEGACY_WORKFLOW_LINK.encode(), config)
        for name in self.gov.RETIRED_ROLES:
            self.assertNotIn(f"[agents.{name}]".encode(), config)
        before = self.snapshot()
        self.init()
        self.assertEqual(self.snapshot(), before)

    def test_old_and_partially_flat_standard_layout_migrates_without_relinking(self):
        self.legacy()
        existing = (self.root / self.tx.WORKFLOW_LINK, self.root / ".agents/skills/sdd-bugfix")
        self.tx.create_workflow_link(existing[0], self.shared)
        self.tx.create_workflow_link(existing[1], self.shared / "skills/sdd-bugfix")
        before = [self.tx.link_snapshot(path) for path in existing]
        self.init()
        self.assert_layout()
        self.assertEqual([self.tx.link_snapshot(path) for path in existing], before)

    def test_unmanaged_alias_to_old_role_path_is_migrated(self):
        self.legacy()
        path = self.root / ".codex/config.toml"
        path.write_bytes(path.read_bytes() + (
            f'\r\n[agents.my_alias]\r\nconfig_file = "{self.gov.legacy_role_reference("sdd-coder")}"\r\n'
        ).encode())
        self.init()
        self.assertIn(self.gov.role_reference("sdd-coder").encode(), path.read_bytes())
        self.assertIn(b"[agents.my_alias]", path.read_bytes())
        self.assert_layout()

    def test_inline_legacy_role_alias_is_migrated_and_retired_alias_removed(self):
        self.legacy()
        path = self.root / ".codex/config.toml"
        path.write_text('[agents]\n'
                        'my_alias = { config_file = "../.agents/skills/sdd-workflow/agents/sdd-coder.toml" }\n'
                        'retired = { config_file = "../.agents/skills/sdd-workflow/agents/sdd-designer.toml" }\n'
                        'other = { config_file = "agents/other.toml" }\n', encoding="utf-8")
        self.init()
        import tomllib
        roles = tomllib.loads(path.read_text(encoding="utf-8"))["agents"]
        self.assertEqual(roles["my_alias"]["config_file"], self.gov.role_reference("sdd-coder"))
        self.assertNotIn("retired", roles)
        self.assertEqual(roles["other"]["config_file"], "agents/other.toml")

    def test_root_inline_legacy_alias_is_migrated(self):
        self.legacy()
        path = self.root / ".codex/config.toml"
        path.write_text('agents = { my_alias = { config_file = '
                        '"../.agents/skills/sdd-workflow/agents/sdd-coder.toml" } }\n'
                        'model = "keep"\n', encoding="utf-8")
        self.init()
        import tomllib
        config = tomllib.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(config["model"], "keep")
        self.assertEqual(config["agents"]["my_alias"]["config_file"], self.gov.role_reference("sdd-coder"))

    def test_old_layout_uses_remembered_hashes_even_without_history(self):
        self.legacy(state=True)
        self.assertFalse((self.skill / "assets/managed-agents-history.json").exists())
        self.init()
        self.assert_layout()

    def test_custom_navigation_and_managed_role_references_are_replaced(self):
        self.legacy()
        for relative, old, new in (
            ("AGENTS.md", b"## Skill", b"Project customization\r\n## Skill"),
            (".codex/config.toml", self.gov.legacy_role_reference("sdd-coder").encode(), b"custom/coder.toml"),
        ):
            path = self.root / relative
            original = path.read_bytes()
            self.assertIn(old, original)
            path.write_bytes(original.replace(old, new))
        self.init()
        self.assert_layout()
        self.assertNotIn(b"Project customization", (self.root / "AGENTS.md").read_bytes())
        self.assertIn(self.gov.role_reference("sdd-coder").encode(),
                      (self.root / ".codex/config.toml").read_bytes())

    def test_real_directories_and_files_are_replaced(self):
        for index, relative in enumerate(self.tx.INSTALL_LINKS):
            for kind in ("directory", "file"):
                with self.subTest(path=relative, kind=kind):
                    project = self.home / f"force-entry-{index}-{kind}"
                    project.mkdir()
                    path = self.tx.link_path(project, relative)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if kind == "directory":
                        path.mkdir()
                        (path / "keep").write_bytes(b"project")
                    else:
                        path.write_bytes(b"project")
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.gov.cmd_init(project, self.args)
                    if relative == self.tx.LEGACY_WORKFLOW_LINK:
                        self.assertFalse(path.exists())
                    else:
                        self.assertTrue(self.tx.linked(path))
        self.assertEqual(self.shared_files(), self.shared_before)

    def test_interrupted_directory_replacement_restores_original(self):
        path = self.tx.link_path(self.root, ".agents/skills/sdd-develop")
        path.mkdir(parents=True)
        (path / "keep.txt").write_bytes(b"project-owned")
        before = self.tx.link_snapshot(path)
        self.crash('''
original = tx.publish_workflow_link
def stop(source, destination):
    if destination.name == 'sdd-develop': os._exit(79)
    return original(source, destination)
tx.publish_workflow_link = stop
''')
        self.recover()
        self.assertEqual(self.tx.link_snapshot(path), before)
        self.assertEqual((path / "keep.txt").read_bytes(), b"project-owned")

    def test_replaced_directory_does_not_remove_nested_link_target(self):
        outside = self.home / "outside-nested"
        outside.mkdir()
        (outside / "keep.txt").write_bytes(b"outside")
        path = self.tx.link_path(self.root, ".agents/skills/sdd-develop")
        path.mkdir(parents=True)
        self.tx.create_workflow_link(path / "external", outside)
        self.init()
        self.assertEqual((outside / "keep.txt").read_bytes(), b"outside")

    def test_interrupted_backup_cleanup_resumes_and_protects_external_edits(self):
        path = self.tx.link_path(self.root, ".agents/skills/sdd-develop")
        path.mkdir(parents=True)
        (path / "first.txt").write_bytes(b"first")
        (path / "second.txt").write_bytes(b"second")
        def interrupt_cleanup(folder):
            (folder / "first.txt").unlink()
            raise OSError("interrupted backup cleanup")
        with patch.object(self.tx.shutil, "rmtree", side_effect=interrupt_cleanup):
            with self.assertRaisesRegex(OSError, "interrupted backup cleanup"):
                self.init()
        backup = next((self.root / self.tx.RECOVERY).glob("old-*"))
        extra = backup / "external.txt"
        extra.write_bytes(b"external edit")
        with self.assertRaisesRegex(ValueError, "External modification"):
            self.recover()
        self.assertEqual(extra.read_bytes(), b"external edit")
        extra.unlink()
        self.recover()
        self.assertTrue((path / "SKILL.md").samefile(self.shared / "skills/sdd-develop/SKILL.md"))
        self.assertFalse((self.root / self.tx.RECOVERY).exists())

    def test_interrupted_nested_alias_removal_restores_original(self):
        path = self.root / ".agents/skills/custom/nested/SKILL.md"
        path.parent.mkdir(parents=True)
        data = b"---\nname: sdd-bugfix\n---\nlocal\n"
        path.write_bytes(data)
        self.crash('''
original = Path.rename
def stop(path, destination):
    result = original(path, destination)
    if path.name == 'SKILL.md' and destination.name.startswith('old-'): os._exit(79)
    return result
Path.rename = stop
''')
        self.recover()
        self.assertEqual(path.read_bytes(), data)

    def test_foreign_and_dangling_links_are_replaced_without_touching_targets(self):
        outside = self.home / "foreign"
        outside.mkdir()
        (outside / "keep").write_bytes(b"outside")
        for index, relative in enumerate(self.tx.INSTALL_LINKS):
            for kind in ("foreign", "dangling"):
                with self.subTest(path=relative, kind=kind):
                    project = self.home / f"force-link-{index}-{kind}"
                    project.mkdir()
                    path = self.tx.link_path(project, relative)
                    target = outside if kind == "foreign" else self.home / f"missing-{index}"
                    target.mkdir(exist_ok=True)
                    self.tx.create_workflow_link(path, target)
                    if kind == "dangling":
                        target.rmdir()
                    with contextlib.redirect_stdout(io.StringIO()) as output:
                        self.gov.cmd_init(project, self.args)
                    if relative == self.tx.LEGACY_WORKFLOW_LINK:
                        self.assertFalse(self.tx.linked(path))
                    else:
                        self.assertIn(f"UPDATED {relative}", output.getvalue())
                        self.assertEqual(self.tx.workflow_target(path),
                                         self.shared if relative == self.tx.WORKFLOW_LINK
                                         else self.shared / "skills" / path.name)
        self.assertEqual((outside / "keep").read_bytes(), b"outside")

    def test_interrupted_foreign_link_replacement_recovers_original(self):
        outside = self.home / "foreign"
        outside.mkdir()
        (outside / "keep").write_bytes(b"outside")
        path = self.tx.link_path(self.root, ".agents/skills/sdd-develop")
        self.tx.create_workflow_link(path, outside)
        self.crash('''
original = tx.publish_workflow_link
def stop(source, destination):
    if destination.name == 'sdd-develop': os._exit(79)
    return original(source, destination)
tx.publish_workflow_link = stop
''')
        self.recover()
        self.assertEqual(self.tx.workflow_target(path), outside)
        self.assertEqual((outside / "keep").read_bytes(), b"outside")

    def test_linked_parent_cannot_redirect_installation(self):
        outside = self.home / "foreign-parent"
        outside.mkdir()
        for relative in (".agents", ".agents/skills"):
            with self.subTest(path=relative):
                path = self.root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                self.tx.create_workflow_link(path, outside)
                with self.assertRaises(ValueError):
                    self.init()
                self.assertEqual(list(outside.iterdir()), [])
                self.tx.remove_workflow_link(path)

    def test_nested_alias_skill_conflict_is_removed(self):
        path = self.root / ".agents/skills/custom/nested/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("---\nname: sdd-bugfix\n---\nlocal\n", encoding="utf-8")
        self.init()
        self.assertFalse(path.exists())
        self.assertTrue((self.root / ".agents/skills/sdd-bugfix/SKILL.md").samefile(
            self.shared / "skills/sdd-bugfix/SKILL.md"))

    def test_partial_link_creation_failure_rolls_back(self):
        original = self.tx.create_workflow_link
        count = 0

        def fail(path, target):
            nonlocal count
            original(path, target)
            count += 1
            if count == 4:
                raise OSError("partial multi-link failure")

        with patch.object(self.tx, "create_workflow_link", side_effect=fail):
            with self.assertRaisesRegex(OSError, "partial multi-link"):
                self.init()
        self.assertEqual(self.snapshot(), {})
        self.assertFalse((self.root / ".agents").exists())
        self.assertFalse((self.root / self.tx.RECOVERY).exists())
        self.assertEqual(self.shared_files(), self.shared_before)
        self.init()
        self.assert_layout()

    def test_process_exit_after_some_links_recovers_all(self):
        self.crash_after_publications()
        self.assertTrue((self.root / self.tx.WORKFLOW_LINK).is_dir())
        self.assertTrue(self.recover())
        self.assertFalse(self.recover())
        self.assertEqual(self.snapshot(), {})
        self.assertEqual(self.shared_files(), self.shared_before)
        self.init()
        self.assert_layout()

    def test_process_exit_after_staging_before_identity_save_recovers(self):
        self.crash('''
original = tx.create_workflow_link
def stop(path, target):
    original(path, target)
    os._exit(79)
tx.create_workflow_link = stop
''')
        self.assertTrue(self.recover())
        self.assertEqual(self.snapshot(), {})
        self.assertEqual(self.shared_files(), self.shared_before)

    def test_failure_after_old_link_deletion_restores_old_layout(self):
        legacy = self.legacy()
        before = self.snapshot()
        original = self.tx.remove_workflow_link

        def fail(path):
            original(path)
            if path == legacy:
                raise OSError("after legacy deletion")

        with patch.object(self.tx, "remove_workflow_link", side_effect=fail):
            with self.assertRaisesRegex(OSError, "legacy deletion"):
                self.init()
        self.assertEqual(self.snapshot(), before)
        self.assertTrue(legacy.samefile(self.shared))
        self.assertEqual(self.shared_files(), self.shared_before)
        self.init()
        self.assert_layout()

    def crash_after_legacy_deletion(self):
        self.crash('''
original = tx.remove_workflow_link
def stop(path):
    original(path)
    if path == root / tx.LEGACY_WORKFLOW_LINK: os._exit(79)
tx.remove_workflow_link = stop
''')

    def test_process_exit_after_old_link_deletion_recovers_before_next_init(self):
        self.legacy()
        before = self.snapshot()
        self.crash_after_legacy_deletion()
        (self.root / "AGENTS.override.md").write_bytes(b"<!-- sdd-contract-governance:start -->\n")
        with self.assertRaisesRegex(ValueError, "不完整"):
            self.init()
        (self.root / "AGENTS.override.md").unlink()
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.shared_files(), self.shared_before)

    def test_restore_failure_keeps_journal_and_can_resume(self):
        self.legacy()
        before = self.snapshot()
        self.crash_after_legacy_deletion()
        original = self.tx.publish_workflow_link

        def fail(source, destination):
            if Path(destination) == self.root / self.tx.LEGACY_WORKFLOW_LINK:
                raise OSError("restore temporarily blocked")
            return original(source, destination)

        with patch.object(self.tx, "publish_workflow_link", side_effect=fail):
            with self.assertRaisesRegex(ValueError, "Recovery blocked"):
                self.recover()
        self.assertTrue((self.root / self.tx.RECOVERY / "journal.json").is_file())
        self.assertTrue(self.recover())
        self.assertEqual(self.snapshot(), before)

    def test_process_exit_during_old_link_restore_can_resume(self):
        self.legacy()
        before = self.snapshot()
        self.crash_after_legacy_deletion()
        self.crash('''
original = tx.publish_workflow_link
def stop(source, destination):
    original(source, destination)
    if destination == root / tx.LEGACY_WORKFLOW_LINK: os._exit(79)
tx.publish_workflow_link = stop
''', command="recover")
        self.assertTrue((self.root / self.tx.LEGACY_WORKFLOW_LINK).samefile(self.shared))
        self.assertTrue(self.recover())
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.shared_files(), self.shared_before)

    def test_external_replacement_blocks_recovery_even_to_same_target(self):
        for same_target in (False, True):
            with self.subTest(same_target=same_target):
                self.crash_after_publications()
                path = self.root / self.tx.WORKFLOW_LINK
                other = self.home / "replacement"
                target = self.shared if same_target else self.home / "foreign-target"
                target.mkdir(exist_ok=True)
                self.tx.create_workflow_link(other, target)
                self.tx.remove_workflow_link(path)
                other.rename(path)
                before = self.snapshot()
                with self.assertRaisesRegex(ValueError, "External modification"):
                    self.recover()
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.shared_files(), self.shared_before)
                self.tx.remove_workflow_link(path)
                self.assertTrue(self.recover())
                self.assertEqual(self.snapshot(), {})

    def test_external_entity_directory_blocks_recovery_without_recursive_delete(self):
        self.crash_after_publications()
        path = self.root / self.tx.WORKFLOW_LINK
        self.tx.remove_workflow_link(path)
        path.mkdir()
        (path / "keep").write_bytes(b"external directory")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "Recovery blocked"):
            self.recover()
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.shared_files(), self.shared_before)

    def test_external_staging_directory_blocks_recovery_without_touching_files(self):
        self.crash('''
original = tx.create_workflow_link
def stop(path, target):
    original(path, target)
    os._exit(79)
tx.create_workflow_link = stop
''')
        stage = self.root / self.tx.RECOVERY / "link-0"
        self.tx.remove_workflow_link(stage)
        stage.mkdir()
        (stage / "keep").write_bytes(b"external staging data")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "Recovery blocked"):
            self.recover()
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.shared_files(), self.shared_before)
        (stage / "keep").unlink()
        stage.rmdir()
        self.recover()
        self.assertEqual(self.snapshot(), {})

    def test_mixed_version_journal_is_rejected_without_changes(self):
        self.crash_after_publications()
        path = self.root / self.tx.RECOVERY / "journal.json"
        original = path.read_bytes()
        journal = json.loads(original)
        journal["workflow_target"] = str(self.shared)
        path.write_text(json.dumps(journal), encoding="utf-8")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "Mixed recovery"):
            self.recover()
        self.assertEqual(self.snapshot(), before)
        path.write_bytes(original)
        self.recover()
        self.assertEqual(self.snapshot(), {})

    def test_late_external_link_before_publication_is_not_removed(self):
        path = self.root / self.tx.WORKFLOW_LINK
        original = self.tx.save
        changed = False

        def edit(folder, journal):
            nonlocal changed
            original(folder, journal)
            if journal.get("links_started") == 1 and not changed:
                changed = True
                self.tx.create_workflow_link(path, self.shared)

        with patch.object(self.tx, "save", side_effect=edit):
            with self.assertRaisesRegex(ValueError, "Recovery blocked"):
                self.init()
        self.assertTrue(path.samefile(self.shared))
        self.assertTrue((self.root / self.tx.RECOVERY).is_dir())
        self.tx.remove_workflow_link(path)
        self.recover()
        self.assertEqual(self.snapshot(), {})

    def test_preflight_replacement_of_an_existing_link_is_detected(self):
        self.init()
        original = self.tx.apply
        path = self.root / ".agents/skills/sdd-bugfix"
        replacement = self.home / "replacement"
        self.tx.create_workflow_link(replacement, self.shared / "skills/sdd-bugfix")

        def edit(root, files, **kwargs):
            self.tx.remove_workflow_link(path)
            replacement.rename(path)
            return original(root, files, **kwargs)

        with patch.object(self.tx, "apply", side_effect=edit):
            with self.assertRaisesRegex(ValueError, "预检后变化"):
                self.init()
        self.assertTrue(path.samefile(self.shared / "skills/sdd-bugfix"))
        self.assertFalse((self.root / self.tx.RECOVERY).exists())

    def test_committed_crash_keeps_successful_new_layout(self):
        self.legacy()
        self.crash('''
original = tx.save
def stop(folder, journal):
    original(folder, journal)
    if journal["state"] == "committed": os._exit(79)
tx.save = stop
''')
        self.assertTrue(self.recover())
        self.assert_layout()
        before = self.snapshot()
        self.init()
        self.assertEqual(self.snapshot(), before)

    def test_old_v1_and_v2_journals_recover_only_the_old_anchor(self):
        for version in (1, 2):
            with self.subTest(version=version):
                legacy = self.tx.link_path(self.root, self.tx.LEGACY_WORKFLOW_LINK)
                self.tx.create_workflow_link(legacy, self.shared)
                anchor = self.tx.workflow_path(self.root)
                self.tx.create_workflow_link(anchor, self.shared)
                (self.root / "AGENTS.md").write_bytes(b"partial old install")
                folder = self.root / self.tx.RECOVERY
                folder.mkdir()
                journal = {"version": version, "root": str(self.root), "state": "prepared",
                           "files": [{"path": "AGENTS.md", "mode": 0o644,
                                      "before": None, "after": self.tx.encode(b"partial old install")}],
                           "directories": [".agents/skills"], "workflow_target": str(self.shared)}
                if version == 2:
                    journal.update(started=1, link_started=True)
                self.tx.save(folder, journal)
                self.assertTrue(self.recover())
                self.assertFalse(self.tx.linked(legacy))
                self.assertTrue(anchor.samefile(self.shared))
                self.assertFalse((self.root / "AGENTS.md").exists())
                self.tx.remove_workflow_link(anchor)
                self.assertEqual(self.shared_files(), self.shared_before)

    def test_historical_journals_preserve_foreign_old_link(self):
        outside = self.home / "foreign"
        outside.mkdir()
        for version in (1, 2):
            with self.subTest(version=version):
                legacy = self.tx.link_path(self.root, self.tx.LEGACY_WORKFLOW_LINK)
                self.tx.create_workflow_link(legacy, outside)
                folder = self.root / self.tx.RECOVERY
                folder.mkdir()
                journal = {"version": version, "root": str(self.root), "state": "prepared",
                           "files": [], "directories": [], "workflow_target": str(self.shared)}
                if version == 2:
                    journal.update(started=0, link_started=True)
                self.tx.save(folder, journal)
                before = self.snapshot()
                with self.assertRaisesRegex(ValueError, "External modification"):
                    self.recover()
                self.assertEqual(self.snapshot(), before)
                self.tx.remove_workflow_link(legacy)
                self.recover()
        self.assertEqual(self.shared_files(), self.shared_before)

    def test_old_v2_unstarted_link_and_committed_journal_keep_old_link(self):
        legacy = self.tx.link_path(self.root, self.tx.LEGACY_WORKFLOW_LINK)
        self.tx.create_workflow_link(legacy, self.shared)
        for state, link_started in (("prepared", False), ("committed", True)):
            folder = self.root / self.tx.RECOVERY
            folder.mkdir()
            self.tx.save(folder, {"version": 2, "root": str(self.root), "state": state,
                                  "files": [], "directories": [], "started": 0,
                                  "link_started": link_started, "workflow_target": str(self.shared)})
            self.assertTrue(self.recover())
            self.assertTrue(legacy.samefile(self.shared))


if __name__ == "__main__":
    unittest.main()
