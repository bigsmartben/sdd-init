"""Isolation and provenance checks for model-evaluation preparation.

These checks do not execute a model or assign behavior-evaluation results.
"""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

import prepare_skill_behavior as prepare


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.folder = Path(self.directory.name)
        self.candidate = self.folder / "candidate"
        rule = self.candidate / ".agents/sdd/references/delegation.md"
        rule.parent.mkdir(parents=True)
        rule.write_text("候选规则\n", encoding="utf-8")
        self.rule = rule
        self.case = {"id": "sample", "input": "普通用户任务", "files": {"src/example.py": "value = 1\n"},
                     "expected": ["EVALUATOR_EXPECTED_SENTINEL"], "forbidden": ["EVALUATOR_FORBIDDEN_SENTINEL"]}

    def test_actor_receives_candidate_bytes_without_evaluation_answers(self):
        before = self.rule.read_bytes()
        output = self.folder / "run"
        project = prepare.prepare_case(self.case, output, candidate=self.candidate)
        self.assertEqual((project / ".agents/sdd/references/delegation.md").read_bytes(), before)
        self.assertEqual((project / "TASK.txt").read_text(encoding="utf-8"), "普通用户任务\n")
        actor_bytes = b"\n".join(path.read_bytes() for path in project.rglob("*") if path.is_file())
        self.assertNotIn(b"EVALUATOR_EXPECTED_SENTINEL", actor_bytes)
        self.assertNotIn(b"EVALUATOR_FORBIDDEN_SENTINEL", actor_bytes)
        self.assertFalse((project / "evaluation.json").exists())
        evaluation = json.loads((output / "evaluation.json").read_text(encoding="utf-8"))
        self.assertEqual(evaluation["expected"], self.case["expected"])
        self.assertEqual(evaluation["model_execution"], "UNVERIFIED")
        manifest = json.loads((output / "candidate-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["files"][".agents/sdd/references/delegation.md"], hashlib.sha256(before).hexdigest())
        self.assertTrue(manifest["preparation_only"])
        self.assertEqual(self.rule.read_bytes(), before)

    def test_invalid_fixture_paths_rejected_before_output_creation(self):
        for number, path in enumerate(("../escape.py", "/absolute.py", "C:/absolute.py", "x\\escape.py", "./file.py", "dir//file.py", ".")):
            with self.subTest(path=path):
                output = self.folder / f"invalid-{number}"
                case = dict(self.case, files={path: "forbidden"})
                with self.assertRaises(ValueError):
                    prepare.prepare_case(case, output, candidate=self.candidate)
                self.assertFalse(output.exists())
        output = self.folder / "invalid-fixture"
        with self.assertRaises(ValueError):
            prepare.prepare_case(dict(self.case, fixture="../outside"), output, candidate=self.candidate)
        self.assertFalse(output.exists())
        output = self.folder / "file-parent-conflict"
        with self.assertRaisesRegex(ValueError, "shadows a parent"):
            prepare.prepare_case(dict(self.case, files={"src": "file", "src/example.py": "code"}), output, candidate=self.candidate)
        self.assertFalse(output.exists())

    def test_existing_output_is_preserved_and_shared_fixture_cannot_replace_rules(self):
        output = self.folder / "existing"
        output.mkdir()
        sentinel = output / "keep.txt"
        sentinel.write_bytes(b"keep")
        with self.assertRaises(FileExistsError):
            prepare.prepare_case(self.case, output, candidate=self.candidate)
        self.assertEqual(list(output.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_bytes(), b"keep")
        corpus = self.folder / "corpus"
        replacement = corpus / "projects/fixture/.agents/sdd/references/delegation.md"
        replacement.parent.mkdir(parents=True)
        replacement.write_text("replacement", encoding="utf-8")
        output = self.folder / "rule-replacement"
        with self.assertRaisesRegex(ValueError, "override candidate rules"):
            prepare.prepare_case(dict(self.case, fixture="projects/fixture"), output, candidate=self.candidate, corpus=corpus)
        self.assertFalse(output.exists())

    def test_real_shared_fixture_copies_without_modifying_seed_or_reporting_pass(self):
        cases = prepare.load_cases()
        case = cases["collaboration_blind_workflow"]
        fixture = prepare.CORPUS / case["fixture"]
        before = prepare.tree_files(fixture)
        output = self.folder / "real-fixture"
        project = prepare.prepare_case(case, output, candidate=self.candidate)
        self.assertEqual((project / "src/order_service.py").read_bytes(), before["src/order_service.py"])
        self.assertEqual(prepare.tree_files(fixture), before)
        self.assertEqual(json.loads((output / "evaluation.json").read_text(encoding="utf-8"))["model_execution"], "UNVERIFIED")

    def test_role_fixture_registers_only_the_selected_role_without_workflow_skills(self):
        cases = prepare.load_cases()
        case_ids = ("role_product_manager", "role_architect", "role_coder", "role_devops", "role_doc_consistency")
        for case_id in case_ids:
            with self.subTest(case=case_id):
                case = cases[case_id]
                output = self.folder / case_id
                project = prepare.prepare_case(case, output)
                role = case["role"]
                config = tomllib.loads((project / ".codex/config.toml").read_text(encoding="utf-8"))
                self.assertEqual(config["agents"][role], {"config_file": f"agents/{role}.toml"})
                self.assertEqual(set(config["agents"]) - {"max_depth", "max_threads"}, {role})
                self.assertEqual([p.stem for p in (project / ".codex/agents").glob("*.toml")], [role])
                self.assertFalse((project / ".codex/agents/review-prompt").exists())
                self.assertEqual(list((project / ".agents/skills").rglob("SKILL.md")), [])
                shared = project / ".agents/sdd-workflow/sdd"
                self.assertTrue((shared / "references/sdd-repository-governance.md").is_file())
                self.assertTrue((shared / "references/document-writing.md").is_file())
                manifest = json.loads((output / "candidate-manifest.json").read_text(encoding="utf-8"))
                self.assertNotIn("docs/index.md", manifest["files"])
                for path, checksum in manifest["files"].items():
                    self.assertEqual(hashlib.sha256((project / path).read_bytes()).hexdigest(), checksum)
                self.assertFalse((project / "evaluation.json").exists())
        invalid = dict(cases["role_doc_consistency"], files={".agents/skills/extra/SKILL.md": "extra"})
        with self.assertRaisesRegex(ValueError, "override candidate rules"):
            prepare.prepare_case(invalid, self.folder / "contaminated-role-fixture")

    def test_main_cases_keep_distributed_entry_roles_and_evaluation_separate(self):
        cases = prepare.load_cases()
        case_ids = ("main_simple", "main_specialist", "main_explore", "main_dependency",
                    "main_gap", "main_goal_change", "main_blocked",
                    "deliver_solo_workflow_setup", "deliver_team_existing_workflow")
        for case_id in case_ids:
            with self.subTest(case=case_id):
                output = self.folder / case_id
                project = prepare.prepare_case(cases[case_id], output)
                entry = (project / "AGENTS.md").read_bytes()
                for name in ("agents-fragment.md",):
                    self.assertIn((prepare.MAIN_ASSETS / name).read_bytes(), entry)
                shared = project / ".agents/sdd-workflow/sdd/references/delegation.md"
                self.assertEqual(shared.read_bytes(), (prepare.ROOT / "source/project/.agents/sdd/references/delegation.md").read_bytes())
                config = tomllib.loads((project / ".codex/config.toml").read_text(encoding="utf-8"))
                for role, reference in config["agents"].items():
                    role_path = project / ".codex" / reference["config_file"]
                    self.assertEqual(tomllib.loads(role_path.read_text(encoding="utf-8"))["name"], role)
                self.assertTrue((project / ".agents/skills/sdd-bugfix/SKILL.md").is_file())
                manifest = json.loads((output / "candidate-manifest.json").read_text(encoding="utf-8"))
                for path, checksum in manifest["files"].items():
                    self.assertEqual(hashlib.sha256((project / path).read_bytes()).hexdigest(), checksum)
                self.assertIn("AGENTS.md", manifest["files"])
                self.assertFalse((project / "evaluation.json").exists())
                self.assertEqual(manifest["model_execution"], "UNVERIFIED")
                self.assertEqual((project / "TASK.txt").read_text(encoding="utf-8"), cases[case_id]["input"] + "\n")
                self.assertTrue((project / ".agents/sdd-workflow/sdd").samefile(project / ".agents/sdd"))
                self.assertTrue((project / ".agents/sdd-workflow/agents").samefile(project / ".codex/agents"))
                checked = subprocess.run(
                    [sys.executable, "-B", str(project / ".agents/sdd/scripts/doc_check.py"),
                     "--root", str(project), "AGENTS.md", ".agents/skills"],
                    capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_full_fixtures_include_the_review_prompt_contract_and_companion(self):
        role_dir = prepare.ROOT / "source/project/.codex/agents"
        role = tomllib.loads((role_dir / "review-prompt.toml").read_text(encoding="utf-8"))
        instructions = role["developer_instructions"].strip() + "\n"
        rules = (role_dir / "review-prompt/prompt-review.md").read_bytes()
        for scope in ("main", "project"):
            with self.subTest(scope=scope):
                case = dict(self.case, candidate_scope=scope)
                project = prepare.prepare_case(case, self.folder / scope)
                shared = project / ".agents/sdd-workflow/roles/shared"
                contract = shared / "review-prompt.md"
                self.assertTrue(contract.is_file(), contract)
                self.assertEqual(contract.read_text(encoding="utf-8"), instructions)
                self.assertEqual((shared / "review-prompt/prompt-review.md").read_bytes(), rules)
                manifest = json.loads((self.folder / scope / "candidate-manifest.json").read_text(encoding="utf-8"))
                for path in (contract, shared / "review-prompt/prompt-review.md"):
                    self.assertEqual(manifest["files"][path.relative_to(project).as_posix()],
                                     hashlib.sha256(path.read_bytes()).hexdigest())

    def test_full_fixture_cannot_replace_generated_review_contract(self):
        case = dict(self.case, fixture=prepare.load_cases()["collaboration_blind_workflow"]["fixture"],
                    files={".agents/sdd-workflow/roles/shared/review-prompt.md": "replacement"})
        for scope in ("main", "project"):
            with self.subTest(scope=scope):
                with self.assertRaisesRegex(ValueError, "override candidate rules"):
                    prepare.prepare_case(dict(case, candidate_scope=scope), self.folder / scope)
                self.assertFalse((self.folder / scope).exists())

    def test_prompt_review_uses_project_preset_role_without_user_profile(self):
        cases = prepare.load_cases()
        for case_id in ("review_prompt_read_only", "review_prompt_compare", "review_prompt_revise",
                        "review_prompt_ab_confirmation"):
            with self.subTest(case=case_id):
                output = self.folder / case_id
                project = prepare.prepare_case(cases[case_id], output)
                config = tomllib.loads((project / ".codex/config.toml").read_text(encoding="utf-8"))
                self.assertEqual(config["agents"]["review-prompt"], {"config_file": "agents/review-prompt.toml"})
                self.assertEqual([p.stem for p in (project / ".codex/agents").glob("*.toml")], ["review-prompt"])
                role = project / ".codex/agents/review-prompt.toml"
                self.assertEqual(role.read_bytes(), (prepare.ROOT / "source/project/.codex/agents/review-prompt.toml").read_bytes())
                instructions = tomllib.loads(role.read_text(encoding="utf-8"))["developer_instructions"]
                contract = project / ".agents/sdd-workflow/roles/shared/review-prompt.md"
                self.assertEqual(contract.read_text(encoding="utf-8"), instructions.strip() + "\n")
                reference = re.search(r"\[审查规则与评价\]\(([^)]+)\)", instructions)
                self.assertIsNotNone(reference)
                rules_path = (contract.parent / reference[1]).relative_to(project).as_posix()
                rules = (prepare.ROOT / "source/project/.codex/agents/review-prompt/prompt-review.md").read_bytes()
                self.assertEqual((project / rules_path).read_bytes(), rules)
                relocated = self.folder / f"{case_id}-relocated"
                shutil.copytree(contract.parent, relocated)
                self.assertEqual((relocated / reference[1]).read_bytes(), rules)
                self.assertFalse((relocated / ".agents").exists())
                self.assertFalse((output / "profile").exists())
                manifest = json.loads((output / "candidate-manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(manifest["files"][rules_path], hashlib.sha256(rules).hexdigest())
                self.assertEqual(manifest["role"], "review-prompt")
                self.assertEqual(manifest["model_execution"], "UNVERIFIED")

    def test_review_contract_and_companion_are_available_in_every_retaining_scope(self):
        cases = prepare.load_cases()
        for scope, case in (("role", cases["review_prompt_read_only"]),
                            ("main", cases["main_simple"]),
                            ("project", self.case)):
            with self.subTest(scope=scope):
                output = self.folder / f"contract-{scope}"
                project = prepare.prepare_case(case, output)
                role = project / ".codex/agents/review-prompt.toml"
                instructions = tomllib.loads(role.read_text(encoding="utf-8"))["developer_instructions"]
                contract = project / ".agents/sdd-workflow/roles/shared/review-prompt.md"
                self.assertEqual(contract.read_text(encoding="utf-8"), instructions.strip() + "\n")
                reference = re.search(r"\[审查规则与评价\]\(([^)]+)\)", instructions)
                self.assertIsNotNone(reference)
                source_rules = (role.parent / reference[1]).read_bytes()
                self.assertEqual((contract.parent / reference[1]).read_bytes(), source_rules)
                relocated = self.folder / f"relocated-contract-{scope}"
                shutil.copytree(contract.parent, relocated)
                self.assertEqual((relocated / reference[1]).read_bytes(), source_rules)
                manifest = json.loads((output / "candidate-manifest.json").read_text(encoding="utf-8"))
                for path in (contract, contract.parent / reference[1]):
                    self.assertEqual(manifest["files"][path.relative_to(project).as_posix()],
                                     hashlib.sha256(path.read_bytes()).hexdigest())

    def test_main_entry_cannot_be_replaced_by_fixture_or_single_role(self):
        case = dict(self.case, candidate_scope="main", files={"AGENTS.md": "replacement"})
        with self.assertRaisesRegex(ValueError, "override candidate rules"):
            prepare.prepare_case(case, self.folder / "entry-replacement", candidate=self.candidate)
        self.assertFalse((self.folder / "entry-replacement").exists())
        case = dict(self.case, candidate_scope="main", role="sdd-coder")
        with self.assertRaisesRegex(ValueError, "cannot select a single role"):
            prepare.prepare_case(case, self.folder / "single-role", candidate=self.candidate)
        self.assertFalse((self.folder / "single-role").exists())


if __name__ == "__main__":
    unittest.main()
