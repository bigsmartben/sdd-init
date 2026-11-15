"""Isolation and provenance checks for model-evaluation preparation.

These checks do not execute a model or assign behavior-evaluation results.
"""
import hashlib
import json
from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
