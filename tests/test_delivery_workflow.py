import base64
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.parse
import zipfile


ROOT = Path(__file__).resolve().parent.parent
with patch.object(sys, "path", [str(ROOT / "scripts"), *sys.path]):
    spec = importlib.util.spec_from_file_location("github_delivery", ROOT / "scripts/github_delivery.py")
    delivery = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(delivery)

B, H, C, M = (letter * 40 for letter in "abcd")
REPO = "owner/repo"
BASE = f"repos/{REPO}"
PULL = f"{BASE}/pulls/9"


def archive(sha=M, version="0.8.4", extra=False):
    files = {f"sdd_init-{version}-py3-none-any.whl": b"tested wheel",
             f"sdd_init-{version}.tar.gz": b"tested sdist"}
    manifest = {"sha": sha, "version": version,
                "files": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}}
    files["PROVENANCE.json"] = json.dumps(manifest).encode()
    if extra:
        files["../unexpected"] = b"not allowed"
    result = io.BytesIO()
    with zipfile.ZipFile(result, "w") as bundle:
        for name, data in files.items():
            bundle.writestr(name, data)
    return result.getvalue()


class FakeGitHub:
    def __init__(self, states=("APPROVED",)):
        self.calls = []
        self.base, self.head = B, H
        self.head_version, self.base_version = "0.8.4", "0.8.3"
        self.states, self.reviews = list(states), []
        self.task_state, self.task_count = "completed", 0
        self.workflow_state, self.check_conclusion = "active", "success"
        self.strict, self.enforce_admins, self.draft = True, True, False
        self.active_tasks, self.dispatches = [], []
        self.stale_review, self.dismissed = False, False
        self.stale_after_checks, self.bad_definition = False, False
        self.bad_tree, self.merge_error = False, False
        self.bad_asset, self.tag = False, None
        self.raw, self.published, self.merged = archive(), False, False
        self.assets = []
        self.files = [{"filename": "src/example.py", "status": "modified"}]
        self.repair_files = self.files[:]
        self.repair_commit_files = None
        self.check_source = "head"
        self.delete_on_merge = False
        self.branch_deleted, self.cleanup_race = False, False
        self.cleanup_head = None

    def pr(self):
        return {"state": "closed" if self.merged else "open", "draft": self.draft,
                "head": {"sha": self.head, "ref": "feat/example", "repo": {"full_name": REPO}},
                "base": {"sha": self.base, "ref": "main", "repo": {"full_name": REPO}},
                "merged": self.merged, "merge_commit_sha": M if self.merged else C,
                "changed_files": len(self.files)}

    def absent(self, path):
        self.calls.append(("ABSENT", path, None))
        if self.tag:
            raise delivery.Blocked("Tag already exists")

    def artifact(self, path):
        self.calls.append(("DOWNLOAD", path, None))
        return self.raw

    def delete_branch(self, repo, branch, expected):
        self.calls.append(("LEASE_DELETE", branch, expected))
        if self.cleanup_race:
            self.cleanup_head = "0" * 40
            return False
        self.branch_deleted = True
        return True

    def pages(self, path, key=None):
        self.calls.append(("PAGES", path, None))
        if path == PULL + "/reviews":
            return self.reviews[:]
        if path == PULL + "/files":
            return self.files[:]
        if key == "files":
            return self.repair_files if self.repair_commit_files is None else self.repair_commit_files
        if path.endswith("/comments"):
            return [{"path": "src/example.py", "line": 2, "body": "Fix the incorrect result"}]
        if "/check-runs" in path:
            source = path.split("/commits/")[1].split("/")[0]
            expected = self.head if self.check_source == "head" else C
            if source != expected:
                return []
            return [{"id": index, "name": name, "app": {"slug": "github-actions"},
                     "head_sha": source, "status": "completed", "conclusion": self.check_conclusion}
                    for index, name in enumerate(delivery.CHECKS)]
        if path.endswith("/jobs"):
            return [{"name": name, "status": "completed", "conclusion": "success"} for name in delivery.CHECKS]
        if path.endswith("/artifacts"):
            return [{"id": 30, "name": "release-packages", "expired": False,
                     "digest": "sha256:" + hashlib.sha256(self.raw).hexdigest()}]
        if path.endswith("/assets"):
            return self.assets[:]
        raise AssertionError(f"Unexpected pagination: {path}")

    def request(self, method, path, data=None, binary=False):
        self.calls.append((method, path, data))
        if method == "GET":
            if path == BASE:
                return {"allow_merge_commit": True, "delete_branch_on_merge": self.delete_on_merge}
            if path.endswith("/git/ref/heads/main"):
                return {"object": {"sha": self.base}}
            if "/git/ref/heads/" in path:
                if self.branch_deleted:
                    raise delivery.GitHubError(404, method, path)
                return {"object": {"sha": self.cleanup_head or self.head}}
            if path == PULL:
                return self.pr()
            if path.endswith("/protection"):
                return {"enforce_admins": {"enabled": self.enforce_admins},
                        "required_status_checks": {"strict": self.strict, "contexts": list(delivery.CHECKS)},
                        "required_pull_request_reviews": {"required_approving_review_count": 1}}
            if path.endswith("/workflows/check.yml"):
                return {"state": self.workflow_state, "path": ".github/workflows/check.yml"}
            if "tasks?state=" in path:
                return {"tasks": self.active_tasks}
            if "/contents/pyproject.toml" in path:
                version = self.base_version if path.endswith(B) else self.head_version
                text = f'[project]\nversion = "{version}"\n'
                return {"content": base64.b64encode(text.encode()).decode()}
            if "/compare/" in path:
                return {"status": "ahead", "files": self.repair_files,
                        "commits": [{"sha": self.head}], "total_commits": 1}
            if "/git/commits/" in path:
                sha = path.rsplit("/", 1)[1]
                parents = [B, self.head] if sha in {C, M} else [B]
                tree = "wrong" if sha == M and self.bad_tree else "tested-tree"
                return {"parents": [{"sha": parent} for parent in parents], "tree": {"sha": tree}}
            if "/reviews/" in path:
                review = dict(self.reviews[-1])
                if self.dismissed:
                    review["state"] = "DISMISSED"
                return review
            if "/tasks/" in path:
                if self.task_state == "completed":
                    self.head = ("e" if self.task_count == 1 else "f") * 40
                return {"state": self.task_state}
            if "/actions/runs/" in path:
                run = self.dispatches[int(path.rsplit("/", 1)[1]) - 1]
                if self.stale_after_checks:
                    self.head = "0" * 40
                return {"head_sha": "wrong" if self.bad_definition else run["definition"],
                        "path": ".github/workflows/check.yml", "event": "workflow_dispatch",
                        "status": "completed", "conclusion": "success"}
            if "/git/ref/tags/" in path:
                return {"object": {"sha": self.tag}}
        if method == "POST":
            if path.endswith("/copilot-code-review"):
                index = len(self.reviews)
                review = {"id": index + 1, "node_id": f"review-{index + 1}",
                          "is_copilot_code_review": True, "state": self.states[min(index, len(self.states) - 1)],
                          "commit_id": B if self.stale_review else self.head, "body": "Looks approved"}
                self.reviews.append(review)
                return {"node_id": f"request-{index + 1}", "state": "PENDING"}
            if path.endswith("/tasks"):
                self.task_count += 1
                return {"id": f"task-{self.task_count}", "state": "queued", "html_url": "https://github.com/task"}
            if path.endswith("/dispatches"):
                self.dispatches.append({**data, "definition": self.base})
                return {"workflow_run_id": len(self.dispatches), "html_url": "https://github.com/run"}
            if path.endswith("/git/blobs"):
                return {"sha": "blob"}
            if path.endswith("/git/trees"):
                return {"sha": "tree"}
            if path.endswith("/git/commits"):
                return {"sha": "9" * 40}
            if path.endswith("/git/refs"):
                self.tag = data["sha"]
                return {"ref": data["ref"]}
            if path.endswith("/releases"):
                return {"id": 50, "html_url": "https://github.com/release", "draft": True,
                        "upload_url": "https://uploads.github.com/release/assets{?name,label}"}
            if path.startswith("https://uploads.github.com/"):
                asset = {"state": "uploaded", "size": len(data),
                         "name": urllib.parse.parse_qs(urllib.parse.urlsplit(path).query)["name"][0],
                         "digest": "bad" if self.bad_asset else "sha256:" + hashlib.sha256(data).hexdigest()}
                self.assets.append(asset)
                return asset
        if method == "PUT" and path.endswith("/merge"):
            if self.merge_error:
                raise delivery.GitHubError(409, method, path)
            if data != {"sha": self.head, "merge_method": "merge"}:
                raise AssertionError("Missing merge CAS")
            self.merged, self.base = True, M
            return {"merged": True, "sha": M}
        if method == "PATCH":
            if "/git/refs/heads/" in path:
                self.head, self.head_version = data["sha"], "0.8.4"
                return {}
            if "/releases/" in path:
                self.published = True
                return {"draft": False, "tag_name": "v0.8.4", "html_url": "https://github.com/release"}
        raise AssertionError(f"Unexpected API call: {method} {path}")


class DeliveryWorkflowTests(unittest.TestCase):
    def controller(self, api=None, **config):
        api = api or FakeGitHub()
        return delivery.Delivery(api, REPO, 9, {"enabled": True, "max_repairs": 2, **config}, {},
                                 B, sleep=lambda _: None, attempts=2)

    def test_approved_exact_candidate_merges_by_cas_then_retests_actual_release(self):
        api = FakeGitHub()
        controller = self.controller(api)
        controller.run()
        self.assertTrue(api.published)
        self.assertEqual(controller.receipt["state"], "published")
        self.assertEqual([r["inputs"]["candidate_sha"] for r in api.dispatches], [C, M])
        self.assertEqual(controller.receipt["merged_sha"], M)
        self.assertEqual(controller.receipt["check_run_id"], 2)
        self.assertEqual([r["sha"] for r in controller.receipt["check_runs"]], [C, M])
        self.assertEqual(api.tag, M)
        self.assertTrue(api.branch_deleted)
        self.assertEqual(controller.receipt["cleanup"], "deleted with expected-head lease")
        self.assertNotEqual(controller.receipt["review_request_node"], api.reviews[0]["node_id"])

    def test_ambiguous_new_native_reviews_do_not_authorize_merge(self):
        api = FakeGitHub()
        original = api.pages

        def ambiguous(path, key=None):
            reviews = original(path, key)
            if path == PULL + "/reviews" and reviews:
                return [*reviews, {**reviews[-1], "id": 100, "node_id": "another-review"}]
            return reviews

        api.pages = ambiguous
        with self.assertRaisesRegex(delivery.Blocked, "Multiple new Copilot reviews"):
            self.controller(api).run()
        self.assertFalse(api.merged)

    def test_pending_request_cannot_reuse_an_existing_native_review(self):
        api = FakeGitHub()
        api.reviews.append({"id": 10, "node_id": "existing-review", "state": "COMMENTED",
                            "is_copilot_code_review": True, "commit_id": H})
        original = api.request

        def pending(method, path, data=None, **kwargs):
            if method == "POST" and path.endswith("/copilot-code-review"):
                return {"node_id": "pending-request", "state": "PENDING"}
            return original(method, path, data, **kwargs)

        api.request = pending
        with self.assertRaisesRegex(delivery.Blocked, "Timed out"):
            self.controller(api).run()
        self.assertFalse(api.merged)
        self.assertEqual(api.task_count, 0)

    def test_native_repair_updates_existing_pr_and_requires_fresh_review(self):
        api = FakeGitHub(("COMMENTED", "APPROVED"))
        self.controller(api).run()
        task = next(data for method, path, data in api.calls if method == "POST" and path.endswith("/tasks"))
        self.assertEqual((task["base_ref"], task["head_ref"], task["create_pull_request"]),
                         ("main", "feat/example", False))
        self.assertEqual([r["commit_id"] for r in api.reviews], [H, "e" * 40])
        self.assertEqual(api.task_count, 1)
        self.assertTrue(api.published)

    def test_repair_budget_does_not_reset_on_agent_head_changes(self):
        api = FakeGitHub(("COMMENTED",))
        with self.assertRaisesRegex(delivery.Blocked, "budget exhausted"):
            self.controller(api).run()
        self.assertEqual(api.task_count, 2)
        self.assertEqual(len(api.reviews), 3)
        self.assertFalse(api.merged)

    def test_version_commit_is_fast_forward_and_happens_before_review(self):
        api = FakeGitHub()
        api.head_version = api.base_version
        self.controller(api).run()
        update = next(call for call in api.calls if call[0] == "PATCH" and "/git/refs/heads/" in call[1])
        self.assertFalse(update[2]["force"])
        self.assertEqual(api.reviews[0]["commit_id"], update[2]["sha"])
        commit = next(data for method, path, data in api.calls if method == "POST" and path.endswith("/git/commits"))
        self.assertEqual(commit["parents"], [H])

    def test_preflight_blocks_before_any_billed_or_mutating_action(self):
        for field, value in (("strict", False), ("enforce_admins", False), ("draft", True),
                             ("workflow_state", "disabled_manually"), ("active_tasks", [{"id": "old"}]),
                             ("delete_on_merge", True)):
            with self.subTest(field=field):
                api = FakeGitHub()
                setattr(api, field, value)
                with self.assertRaises(delivery.Blocked):
                    self.controller(api).run()
                self.assertFalse(any(method in {"POST", "PUT", "PATCH"} for method, _, _ in api.calls))

    def test_queued_controller_cannot_use_newer_main_policy(self):
        for changed in ("base", "main"):
            with self.subTest(changed=changed):
                api = FakeGitHub()
                if changed == "base":
                    api.base = "0" * 40
                else:
                    original = api.request

                    def changed_main(method, path, data=None, **kwargs):
                        if path.endswith("/git/ref/heads/main"):
                            return {"object": {"sha": "0" * 40}}
                        return original(method, path, data, **kwargs)

                    api.request = changed_main
                with self.assertRaisesRegex(delivery.Blocked, "controller is stale"):
                    self.controller(api).run()
                self.assertFalse(any(method in {"POST", "PUT", "PATCH", "LEASE_DELETE"}
                                     for method, _, _ in api.calls))

    def test_protected_changes_and_renames_require_independent_integration(self):
        changes = [
            {"filename": ".github/workflows/check.yml", "status": "modified"},
            {"filename": ".github/copilot-instructions.md", "status": "added"},
            {"filename": ".github/agents/fix.agent.md", "status": "removed"},
            {"filename": "src/ordinary.py", "previous_filename": ".github/delivery.json", "status": "renamed"},
            {"filename": ".github/new.yml", "previous_filename": "src/ordinary.py", "status": "renamed"},
            {"filename": "scripts/github_delivery.py", "status": "modified"},
            {"filename": "src/ordinary.py", "previous_filename": "scripts/next_release_version.py", "status": "renamed"},
            {"filename": "scripts/smoke_package.py", "status": "modified"},
            {"filename": "AGENTS.md", "status": "modified"},
            {"filename": ".agents/skills/repair/SKILL.md", "status": "added"},
            {"filename": ".codex/config.toml", "status": "modified"},
        ]
        for stage in ("initial", "repair"):
            for change in changes:
                with self.subTest(stage=stage, change=change):
                    api = FakeGitHub(("COMMENTED", "APPROVED"))
                    if stage == "initial":
                        api.files = [change]
                    else:
                        api.repair_files = [change]
                    with self.assertRaisesRegex(delivery.Blocked, "Protected"):
                        self.controller(api).run()
                    self.assertFalse(api.merged)
                    self.assertFalse(api.published)
                    if stage == "initial":
                        self.assertFalse(any(method in {"POST", "PUT", "PATCH"} for method, _, _ in api.calls))

    def test_repair_cannot_hide_a_protected_change_by_reverting_it(self):
        api = FakeGitHub(("COMMENTED", "APPROVED"))
        api.repair_commit_files = [{"filename": ".github/workflows/check.yml", "status": "modified"}]
        with self.assertRaisesRegex(delivery.Blocked, "Protected"):
            self.controller(api).run()
        self.assertFalse(api.merged)
        self.assertFalse(api.published)

    def test_missing_rename_origin_or_truncated_repair_diff_is_blocked(self):
        for files in ([{"filename": "src/new.py", "status": "renamed"}],
                      [{"filename": f"src/{i}.py", "status": "modified"} for i in range(300)]):
            with self.subTest(files=len(files)):
                api = FakeGitHub(("COMMENTED", "APPROVED"))
                api.repair_files = files
                with self.assertRaises(delivery.Blocked):
                    self.controller(api).run()
                self.assertFalse(api.merged)

    def test_pr_checks_support_head_or_current_test_merge_without_mixing(self):
        for source in ("head", "merge"):
            with self.subTest(source=source):
                api = FakeGitHub()
                api.check_source = source
                controller = self.controller(api)
                controller.run()
                self.assertTrue(api.published)
                self.assertEqual(controller.receipt["pr_check_source_sha"], H if source == "head" else C)

    def test_partial_or_failed_merge_checks_cannot_fall_back_to_green_head(self):
        for partial in (False, True):
            with self.subTest(partial=partial):
                api = FakeGitHub()
                original = api.pages

                def checks(path, key=None):
                    if f"/commits/{C}/check-runs" in path:
                        names = list(delivery.CHECKS)[:1] if partial else list(delivery.CHECKS)
                        return [{"id": i, "name": name, "app": {"slug": "github-actions"}, "head_sha": C,
                                 "status": "completed", "conclusion": "success" if partial else "failure"}
                                for i, name in enumerate(names)]
                    return original(path, key)

                api.pages = checks
                with self.assertRaises(delivery.Blocked):
                    self.controller(api).run()
                self.assertFalse(api.merged)
                self.assertEqual(api.dispatches, [])

    def test_newer_or_racing_branch_is_retained_after_published_release(self):
        for racing in (False, True):
            with self.subTest(racing=racing):
                api = FakeGitHub()
                if racing:
                    api.cleanup_race = True
                else:
                    api.cleanup_head = "0" * 40
                controller = self.controller(api)
                with self.assertRaises(delivery.Blocked):
                    controller.run()
                self.assertTrue(api.published)
                self.assertFalse(api.branch_deleted)
                self.assertEqual(controller.receipt["state"], "published")
                leases = [call for call in api.calls if call[0] == "LEASE_DELETE"]
                self.assertEqual(len(leases), 1 if racing else 0)
                if leases:
                    self.assertEqual(leases[0][2], H)

    def test_unknown_cleanup_outcome_is_not_reported_as_confirmed_deletion(self):
        api = FakeGitHub()

        def unconfirmed(repo, branch, expected):
            api.branch_deleted = True
            return False

        api.delete_branch = unconfirmed
        controller = self.controller(api)
        with self.assertRaisesRegex(delivery.Blocked, "outcome is unconfirmed"):
            controller.run()
        self.assertTrue(api.published)
        self.assertEqual(controller.receipt["state"], "published")
        self.assertEqual(controller.receipt["cleanup"], "absent after an unconfirmed cleanup attempt")

    def test_auto_delete_reenabled_during_checks_blocks_merge(self):
        api = FakeGitHub()
        original = api.request

        def changed_policy(method, path, data=None, **kwargs):
            result = original(method, path, data, **kwargs)
            if "/actions/runs/" in path:
                api.delete_on_merge = True
            return result

        api.request = changed_policy
        with self.assertRaisesRegex(delivery.Blocked, "auto-delete"):
            self.controller(api).run()
        self.assertFalse(api.merged)

    def test_real_git_cleanup_lease_deletes_only_the_expected_remote_head(self):
        git = shutil.which("git")
        if not git:
            self.skipTest("Git is required to verify receive-pack lease semantics")
        real_run = subprocess.run
        for advanced in (False, True):
            with self.subTest(advanced=advanced), tempfile.TemporaryDirectory(prefix=".delivery-test-", dir=ROOT) as directory:
                remote, client = Path(directory) / "remote.git", Path(directory) / "client.git"
                env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
                for folder in (remote, client):
                    real_run([git, "init", "--bare", str(folder)], env=env, capture_output=True, check=True)

                def run_git(*args, input=None):
                    result = real_run([git, f"--git-dir={remote}", *args], input=input, text=True,
                                      env=env, capture_output=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    return result.stdout.strip()

                tree = run_git("hash-object", "-w", "-t", "tree", "--stdin", input="")
                identity = ("-c", "user.name=Test", "-c", "user.email=test@example.invalid")
                old = run_git(*identity, "commit-tree", tree, "-m", "old")
                new = run_git(*identity, "commit-tree", tree, "-p", old, "-m", "new")
                run_git("update-ref", "refs/heads/feature", new if advanced else old)
                token = "offline-placeholder-not-a-real-token"

                def local_push(args, **kwargs):
                    self.assertIn(f"--force-with-lease=refs/heads/feature:{old}", args)
                    self.assertNotIn(token, " ".join(args))
                    credential = base64.b64encode(f"x-access-token:{token}".encode()).decode()
                    self.assertNotIn(credential, " ".join(args))
                    self.assertIn(credential, kwargs["env"]["GIT_CONFIG_VALUE_1"])
                    self.assertIn(f"https://github.com/{REPO}.git", args)
                    args = [str(remote) if value == f"https://github.com/{REPO}.git" else value for value in args]
                    self.assertFalse(any(value.startswith(("https://", "http://")) for value in args))
                    args.insert(1, f"--git-dir={client}")
                    return real_run(args, cwd=client, **kwargs)

                with patch.object(delivery.subprocess, "run", side_effect=local_push):
                    deleted = delivery.GitHub(token).delete_branch(REPO, "feature", old)
                self.assertEqual(deleted, not advanced)
                result = real_run([git, f"--git-dir={remote}", "rev-parse", "--verify", "refs/heads/feature"],
                                  capture_output=True, text=True, env=env)
                if advanced:
                    self.assertEqual(result.stdout.strip(), new)
                else:
                    self.assertNotEqual(result.returncode, 0)

    def test_stale_reviews_dismissal_cas_and_workflow_fail_closed(self):
        for field in ("stale_review", "dismissed", "bad_definition", "stale_after_checks", "merge_error"):
            with self.subTest(field=field):
                api = FakeGitHub()
                setattr(api, field, True)
                with self.assertRaises(delivery.Blocked):
                    self.controller(api).run()
                self.assertFalse(api.merged)
                self.assertIsNone(api.tag)

    def test_failed_or_unapproved_pr_checks_never_trigger_fallback_dispatch(self):
        for conclusion in ("failure", "action_required", "cancelled", "skipped"):
            with self.subTest(conclusion=conclusion):
                api = FakeGitHub()
                api.check_conclusion = conclusion
                with self.assertRaises(delivery.Blocked):
                    self.controller(api).run()
                self.assertEqual(api.dispatches, [])
                self.assertFalse(api.merged)

    def test_missing_pr_checks_timeout_without_approval_or_retry_api(self):
        api = FakeGitHub()
        original = api.pages
        api.pages = lambda path, key=None: [] if "/check-runs" in path else original(path, key)
        with self.assertRaisesRegex(delivery.Blocked, "Timed out"):
            self.controller(api).run()
        self.assertEqual(api.dispatches, [])

    def test_waiting_idle_failed_cloud_task_does_not_authorize_merge(self):
        for state in ("waiting_for_user", "idle", "failed", "timed_out", "cancelled", "in_progress"):
            with self.subTest(state=state):
                api = FakeGitHub(("COMMENTED", "APPROVED"))
                api.task_state = state
                with self.assertRaises(delivery.Blocked):
                    self.controller(api).run()
                self.assertEqual(api.task_count, 1)
                self.assertFalse(api.merged)

    def test_approval_prose_or_no_findings_is_not_structured_approval(self):
        api = FakeGitHub(("COMMENTED",))
        original = api.pages
        api.pages = lambda path, key=None: [] if path.endswith("/comments") else original(path, key)
        with self.assertRaisesRegex(delivery.Blocked, "No actionable"):
            self.controller(api).run()
        self.assertEqual(api.task_count, 0)
        self.assertFalse(api.merged)

    def test_mismatched_merge_tree_or_artifact_stops_release_after_merge(self):
        for kind in ("tree", "sha", "extra"):
            with self.subTest(kind=kind):
                api = FakeGitHub()
                api.bad_tree = kind == "tree"
                api.raw = archive(sha=H if kind == "sha" else M, extra=kind == "extra")
                controller = self.controller(api)
                with self.assertRaises(delivery.Blocked):
                    controller.run()
                self.assertTrue(api.merged)
                self.assertEqual(controller.receipt["merged_sha"], M)
                self.assertIsNone(api.tag)

    def test_upload_integrity_failure_retains_draft_not_published(self):
        api = FakeGitHub()
        api.bad_asset = True
        controller = self.controller(api)
        with self.assertRaisesRegex(delivery.Blocked, "draft retained"):
            controller.run()
        self.assertEqual(api.tag, M)
        self.assertEqual(controller.receipt["release_id"], 50)
        self.assertFalse(api.published)

    def test_legacy_dispatch_response_without_run_identity_is_blocked(self):
        api = FakeGitHub()
        original = api.request
        api.request = lambda method, path, data=None, **kwargs: None if path.endswith("/dispatches") else original(method, path, data, **kwargs)
        with self.assertRaisesRegex(delivery.Blocked, "no run ID"):
            self.controller(api).run()
        self.assertFalse(api.merged)

    def test_review_api_denials_are_not_retried_or_interpreted_as_success(self):
        for code in (403, 409, 422, 429, 503):
            with self.subTest(code=code):
                api = FakeGitHub()
                original = api.request
                requests = []

                def denied(method, path, data=None, **kwargs):
                    if path.endswith("/copilot-code-review"):
                        requests.append(path)
                        raise delivery.GitHubError(code, method, path)
                    return original(method, path, data, **kwargs)

                api.request = denied
                with self.assertRaises(delivery.Blocked):
                    self.controller(api).run()
                self.assertEqual(len(requests), 1)
                self.assertFalse(api.merged)

    def test_disabled_or_missing_token_writes_failed_receipt_without_network(self):
        for enabled in (False, True):
            with self.subTest(enabled=enabled), tempfile.TemporaryDirectory(prefix=".delivery-test-", dir=ROOT) as directory:
                root = Path(directory)
                (root / ".github").mkdir()
                (root / ".github/delivery.json").write_text(json.dumps({"enabled": enabled, "max_repairs": 2}))
                env = {k: v for k, v in os.environ.items() if k not in {"SDD_DELIVERY_TOKEN", "GITHUB_STEP_SUMMARY"}}
                result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/github_delivery.py")],
                                        cwd=root, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 1)
                receipt = json.loads((root / ".build/delivery/receipt.json").read_text())
                self.assertEqual(receipt["state"], "blocked")
                self.assertIn("Missing required" if enabled else "Delivery disabled", receipt["error"])

    def test_no_default_branch_push_or_pr_creation_entry(self):
        workflow = (ROOT / ".github/workflows/delivery.yml").read_text(encoding="utf-8")
        self.assertNotIn("  push:", workflow)
        self.assertNotIn("synchronize", workflow)
        self.assertNotIn("gh pr create", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("pull_request_target:", workflow)
        self.assertIn("types: [opened, ready_for_review]", workflow)
        self.assertIn("queue: max", workflow)
        self.assertIn("CONTROLLER_SHA: ${{ github.sha }}", workflow)


if __name__ == "__main__":
    unittest.main()
