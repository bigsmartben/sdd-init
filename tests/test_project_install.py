"""Recovery tests use isolated projects, real files and explicit fault injection."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from test_build import WORKFLOW, project_entries, project_files

ROOT = Path(__file__).resolve().parent.parent


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


builder = module(ROOT / "scripts/build_release.py", "recovery_builder")


class ProjectInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build_temp = tempfile.TemporaryDirectory()
        cls.skill = builder.build(Path(cls.build_temp.name) / "skill")

    @classmethod
    def tearDownClass(cls):
        cls.build_temp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        self.gov = module(self.skill / "scripts/govern.py", "candidate_init")
        self.tx = self.gov.transaction
        self.args = self.gov.build_parser().parse_args(["init"])

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in project_files(self.root)}

    def run_init(self, *, env=None, command="init"):
        return subprocess.run([sys.executable, "-B", "-X", "utf8",
                               str(self.skill / "scripts/govern.py"),
                               "--root", str(self.root), command],
                              capture_output=True, text=True, encoding="utf-8", timeout=30, env=env)

    def crash(self, hook):
        # No production fault switches: monkeypatch solely in the child test.
        program = '''
import importlib.util, os, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("crash_init", sys.argv[1])
gov = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gov)
tx = gov.transaction
''' + hook + '''
gov.cmd_init(Path(sys.argv[2]), gov.build_parser().parse_args(["init"]))
'''
        result = subprocess.run([sys.executable, "-B", "-X", "utf8", "-c", program,
                                 str(self.skill / "scripts/govern.py"), str(self.root)],
                                capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 79, result.stderr)

    def test_safe_path_accepts_equivalent_resolved_root_and_rejects_escape(self):
        # Simulate a Windows short-name root resolving to its long-name path.
        original_resolve = Path.resolve
        resolved_root = self.root.parent / "canonical-project"

        def resolve_alias(path, *args, **kwargs):
            if path == self.root:
                return resolved_root
            if path == self.root / ".sdd-init.lock":
                return resolved_root / ".sdd-init.lock"
            return original_resolve(path, *args, **kwargs)

        with patch.object(Path, "resolve", resolve_alias):
            self.assertEqual(self.tx.safe_path(self.root, ".sdd-init.lock"),
                             self.root / ".sdd-init.lock")
            with self.assertRaises(ValueError):
                self.tx.safe_path(self.root, "../outside")

    def test_write_failure_restores_existing_and_new_files(self):
        (self.root / "AGENTS.md").write_bytes(b"personal rules\r\n")
        (self.root / "unrelated.txt").write_bytes(b"keep")
        before = self.snapshot()
        original = self.tx.replace_file
        count = 0

        def fail_partway(folder, path, data, mode=0o644):
            nonlocal count
            if path.name != "journal.json":
                count += 1
                if count == 3:
                    raise OSError("injected write failure")
            return original(folder, path, data, mode)

        with patch.object(self.tx, "replace_file", side_effect=fail_partway):
            with self.assertRaisesRegex(OSError, "injected"):
                self.gov.cmd_init(self.root, self.args)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.root / ".agents").exists())
        self.assertFalse((self.root / self.tx.RECOVERY).exists())
        self.assertEqual(self.run_init().returncode, 0)

    def test_preflight_snapshot_rejects_late_external_edits(self):
        for relative in ("AGENTS.md", ".codex/config.toml"):
            with self.subTest(path=relative):
                target = self.root / relative
                original = self.tx.apply

                def edit_then_apply(root, changes, **kwargs):
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(b"EXTERNAL EDIT")
                    return original(root, changes, **kwargs)

                with patch.object(self.tx, "apply", side_effect=edit_then_apply):
                    with self.assertRaisesRegex(ValueError, "changed after preflight"):
                        self.gov.cmd_init(self.root, self.args)
                self.assertEqual(target.read_bytes(), b"EXTERNAL EDIT")
                self.assertFalse((self.root / self.tx.RECOVERY).exists())
                target.unlink()

    def test_inspect_reports_versions_and_conflicts_without_writes(self):
        result = self.run_init(command="inspect")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Shared version: sha256:", result.stdout)
        self.assertIn("Registered roles: none", result.stdout)
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertEqual(self.run_init().returncode, 0)
        before = self.snapshot()
        result = self.run_init(command="inspect")
        self.assertIn("Project changes on init: none", result.stdout)
        self.assertIn("sdd-architect", result.stdout)
        self.assertEqual(self.snapshot(), before)
        agents = self.root / "AGENTS.md"
        agents.write_bytes(agents.read_bytes().replace(
            b"<!-- sdd-contract-governance:end -->", b"Project-owned entry\n<!-- sdd-contract-governance:end -->",
        ))
        before = self.snapshot()
        for command in ("inspect", "init"):
            result = self.run_init(command=command)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("sdd-contract-governance", result.stderr)
            self.assertEqual(self.snapshot(), before)

    def test_role_and_skill_names_cannot_shadow_shared_entries(self):
        names = {
            ".agents/skills/group/local/SKILL.md": b"---\nname: sdd-develop\ndescription: Custom.\n---\n",
            ".codex/agents/local.toml": b'name = "sdd-architect"\n',
        }
        for relative, data in names.items():
            with self.subTest(path=relative):
                path = self.root / relative
                path.parent.mkdir(parents=True)
                path.write_bytes(data)
                before = self.snapshot()
                result = self.run_init()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(relative, result.stderr)
                self.assertEqual(self.snapshot(), before)
                path.unlink()

    def test_late_edit_to_unwritten_file_does_not_block_rollback(self):
        config = self.root / ".codex/config.toml"
        original = self.tx.replace_file

        def edit_second_file(folder, path, data, mode=0o644):
            original(folder, path, data, mode)
            if path.name == "AGENTS.md":
                config.parent.mkdir()
                config.write_bytes(b"external edit")

        with patch.object(self.tx, "replace_file", side_effect=edit_second_file):
            with self.assertRaisesRegex(ValueError, "File changed during installation"):
                self.gov.cmd_init(self.root, self.args)
        self.assertEqual(self.snapshot(), {".codex/config.toml": b"external edit"})
        self.assertFalse((self.root / self.tx.RECOVERY).exists())

    def test_recover_only_removes_interrupted_install(self):
        self.crash('''
original = tx.create_workflow_link
def stop(path, target):
    original(path, target)
    os._exit(79)
tx.create_workflow_link = stop
''')
        self.assertIn("PENDING", self.run_init(command="inspect").stdout)
        result = self.run_init(command="recover")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("RECOVERED", result.stdout)
        self.assertEqual(self.snapshot(), {})
        self.assertFalse((self.root / WORKFLOW).exists())
        self.assertIn("No pending", self.run_init(command="recover").stdout)

    def test_upgrade_rollback_preserves_customizations_and_history(self):
        self.assertEqual(self.run_init().returncode, 0)
        customized = self.root / ".codex/config.toml"
        customized.write_bytes(b'model = "project-choice"\r\n' + customized.read_bytes().replace(
            b'config_file = "../.agents/skills/sdd-workflow/agents/sdd-coder.toml"',
            b'config_file = "agents/sdd-coder.toml"',
        ))
        history = self.root / "specs/old/status.md"
        history.parent.mkdir(parents=True)
        history.write_bytes(b"historical evidence")
        before = self.snapshot()
        original = self.tx.save

        def fail_commit(folder, journal):
            if journal["state"] == "committed":
                raise OSError("commit failure")
            return original(folder, journal)

        with patch.object(self.tx, "save", side_effect=fail_commit):
            with self.assertRaisesRegex(OSError, "commit failure"):
                self.gov.cmd_init(self.root, self.args)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.run_init().returncode, 0)
        self.assertEqual(history.read_bytes(), b"historical evidence")

    def test_process_exit_is_recovered_before_next_install(self):
        (self.root / "AGENTS.md").write_bytes(b"original\n")
        self.crash('''
original = tx.replace_file
def stop(folder, path, data, mode=0o644):
    original(folder, path, data, mode)
    if path.name == "AGENTS.md": os._exit(79)
tx.replace_file = stop
''')
        self.assertTrue((self.root / self.tx.RECOVERY / "journal.json").exists())
        # A new preflight blocker proves recovery happens before new planning.
        (self.root / "AGENTS.override.md").write_bytes(b"unrelated")
        result = self.run_init()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RECOVERED", result.stdout)
        self.assertEqual((self.root / "AGENTS.md").read_bytes(), b"original\n")
        self.assertFalse((self.root / self.tx.RECOVERY).exists())
        (self.root / "AGENTS.override.md").unlink()
        self.assertEqual(self.run_init().returncode, 0)

    def test_crash_after_link_creation_rolls_back_without_touching_shared_files(self):
        role = "agents/sdd-architect.toml"
        shared = self.skill / "shared" / role
        original = shared.read_bytes()
        self.crash("""
original = tx.create_workflow_link
def stop(path, target):
    original(path, target)
    os._exit(79)
tx.create_workflow_link = stop
""")
        self.assertTrue((self.root / WORKFLOW / role).samefile(shared))
        (self.root / "AGENTS.override.md").write_bytes(b"block next install")
        result = self.run_init()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RECOVERED", result.stdout)
        self.assertFalse((self.root / WORKFLOW).exists())
        self.assertFalse((self.root / ".codex/config.toml").exists())
        self.assertEqual(shared.read_bytes(), original)

    def test_external_edit_blocks_recovery_without_overwrite(self):
        self.crash('''
original = tx.replace_file
def stop(folder, path, data, mode=0o644):
    original(folder, path, data, mode)
    if path.name == "AGENTS.md": os._exit(79)
tx.replace_file = stop
''')
        agents = self.root / "AGENTS.md"
        installed = agents.read_bytes()
        agents.write_bytes(b"external edit after crash")
        before = self.snapshot()
        for _ in range(2):
            result = self.run_init()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Recovery blocked", result.stderr)
            self.assertIn("AGENTS.md", result.stderr)
            self.assertEqual(self.snapshot(), before)
        # Operator explicitly reconciles the conflict; init can now recover.
        agents.write_bytes(installed)
        self.assertEqual(self.run_init().returncode, 0)

    def test_restore_failure_retains_journal_and_can_resume(self):
        agents = self.root / "AGENTS.md"
        agents.write_bytes(b"old")
        original = self.tx.replace_file

        def fail(folder, path, data, mode=0o644):
            if path.name != "journal.json" and (path != agents or data == b"old"):
                raise OSError(f"denied: {path}")
            return original(folder, path, data, mode)

        with patch.object(self.tx, "replace_file", side_effect=fail):
            with self.assertRaisesRegex(ValueError, "Recovery blocked"):
                self.gov.cmd_init(self.root, self.args)
        self.assertTrue((self.root / self.tx.RECOVERY / "journal.json").exists())
        with self.tx.project_lock(self.root):
            self.tx.recover(self.root)
        self.assertEqual(agents.read_bytes(), b"old")
        self.assertEqual(self.run_init().returncode, 0)

    def test_committed_crash_does_not_roll_back_success(self):
        self.crash('''
original = tx.save
def stop(folder, journal):
    original(folder, journal)
    if journal["state"] == "committed": os._exit(79)
tx.save = stop
''')
        installed = {p: b for p, b in self.snapshot().items() if not p.startswith(self.tx.RECOVERY)}
        result = self.run_init()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.snapshot(), installed)

    def test_crash_before_journal_publication_leaves_targets_unchanged(self):
        self.crash('''
def stop(folder, journal): os._exit(79)
tx.save = stop
''')
        self.assertEqual(self.snapshot(), {})
        self.assertEqual(self.run_init().returncode, 0)

    def test_parallel_install_is_rejected_and_lock_released_on_exit(self):
        program = '''
import importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("locking", sys.argv[1])
tx = importlib.util.module_from_spec(spec); spec.loader.exec_module(tx)
with tx.project_lock(Path(sys.argv[2])):
    print("LOCKED", flush=True)
    sys.stdin.readline()
'''
        with subprocess.Popen([sys.executable, "-B", "-X", "utf8", "-c", program,
                               str(self.skill / "scripts/project_install.py"), str(self.root)],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True, encoding="utf-8") as child:
            try:
                self.assertEqual(child.stdout.readline().strip(), "LOCKED")
                other_temp = Path(self.temp.name) / "different-temp"
                other_temp.mkdir()
                env = dict(os.environ, TEMP=str(other_temp), TMP=str(other_temp), TMPDIR=str(other_temp))
                result = self.run_init(env=env)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("installation in progress", result.stderr)
                self.assertEqual(list(self.root.iterdir()), [self.root / ".sdd-init.lock"])
            finally:
                child.kill()
                child.communicate(timeout=10)
        self.assertEqual((self.root / ".sdd-init.lock").read_bytes(), b"\0")
        self.assertEqual(self.run_init().returncode, 0)

    def test_corrupt_journal_blocks_writes(self):
        folder = self.root / self.tx.RECOVERY
        folder.mkdir()
        (folder / "journal.json").write_bytes(b"not json")
        before = self.snapshot()
        result = self.run_init()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Recovery blocked", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_retired_commands_rejected_by_both_installed_tools(self):
        self.assertEqual(self.run_init().returncode, 0)
        history = self.root / "specs/old/status.md"
        history.parent.mkdir(parents=True)
        history.write_bytes(b"original historical evidence")
        before = self.snapshot()
        for script in (self.skill / "scripts/govern.py", self.root / WORKFLOW / "sdd/scripts/govern.py"):
            for cmd in ("start", "record", "attest", "check", "finish", "commit"):
                with self.subTest(script=script, cmd=cmd):
                    result = subprocess.run([sys.executable, "-B", "-X", "utf8", str(script),
                                             "--root", str(self.root), cmd],
                                            capture_output=True, timeout=30)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn(b"invalid choice", result.stderr)
                    self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
