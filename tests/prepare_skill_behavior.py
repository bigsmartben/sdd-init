"""Prepare fresh, isolated model-evaluation workspaces from maintained fixtures.

This copies candidate rules without invoking an installer or a model. Evaluation
criteria remain outside the executor's project; model results are never inferred.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import shutil

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/fixtures/skill-behavior"
MAIN_ASSETS = ROOT / "source/initializer/assets"
REVIEW_SKILL = Path(".agents/skills/sdd-workflow-review")


def relative_path(raw):
    path = PurePosixPath(raw)
    if not raw or path.is_absolute() or any(part in ("..", ".", "") for part in raw.split("/")) or "\\" in raw or ":" in raw:
        raise ValueError(f"Unsafe fixture path: {raw}")
    return path


def load_cases(path=CORPUS / "cases.json"):
    cases = json.loads(path.read_text(encoding="utf-8"))
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate case ID")
    for case in cases:
        relative_path(case["id"])
    return {case["id"]: case for case in cases}


def tree_files(root):
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"Fixture source must be an existing ordinary directory: {root}")
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlink is not a fixture input: {path}")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            result[path.relative_to(root).as_posix()] = path.read_bytes()
    return result


def prepare_case(case, output, *, candidate=ROOT / "source/project", corpus=CORPUS):
    """Create a new case directory after validating every input path."""
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Output already exists: {output}")
    # A linked parent could silently write into an unrelated installation.
    for parent in output.parents:
        if parent.is_symlink():
            raise ValueError(f"Linked output parent: {parent}")
    scope = case.get("candidate_scope", "project")
    if scope in ("project", "main", "review-role"):
        payload = tree_files(candidate)
    elif scope == "workflow-review":
        payload = {f"{REVIEW_SKILL.as_posix()}/{name}": content
                   for name, content in tree_files(ROOT / REVIEW_SKILL).items()}
    else:
        raise ValueError(f"Unknown candidate scope: {scope}")
    selected_role = case.get("role", "review-prompt" if scope == "review-role" else None)
    if scope == "main":
        if selected_role is not None:
            raise ValueError("Main evaluation cannot select a single role")
        payload["AGENTS.md"] = (MAIN_ASSETS / "agents-fragment.md").read_bytes()
        roles = sorted(name for name in payload if name.startswith(".codex/agents/") and name.endswith(".toml"))
        payload[".codex/config.toml"] = "".join(
            f'[agents.{Path(name).stem}]\nconfig_file = "agents/{Path(name).name}"\n'
            for name in roles
        ).encode("utf-8")
    if selected_role is not None:
        role_file = f".codex/agents/{relative_path(selected_role)}.toml"
        if role_file not in payload or "/" in selected_role:
            raise ValueError(f"Unknown role: {selected_role}")
        shared_prefix = ".agents/sdd/"
        installed_prefix = ".agents/sdd-workflow/sdd/"
        payload = {
            installed_prefix + name.removeprefix(shared_prefix) if name.startswith(shared_prefix) else name: content
            for name, content in payload.items()
            if not name.startswith((".agents/skills/", ".codex/")) or name == role_file
        }
    rules = dict(payload)
    if "fixture" in case:
        fixture = corpus / str(relative_path(case["fixture"]))
        if not fixture.is_dir():
            raise ValueError(f"Missing fixture: {fixture}")
        for parent in (fixture, *fixture.parents):
            if parent == corpus.parent:
                break
            if parent.is_symlink():
                raise ValueError(f"Linked fixture path: {parent}")
        payload.update(tree_files(fixture))
    for name, content in case.get("files", {}).items():
        payload[str(relative_path(name))] = content.encode("utf-8")
    for name in payload:
        relative_path(name)
        if any(parent.as_posix() in payload for parent in PurePosixPath(name).parents if str(parent) != "."):
            raise ValueError(f"Fixture file shadows a parent directory: {name}")
    if case.get("fixture") or selected_role is not None or scope != "project":
        for name, content in payload.items():
            if (name.startswith((".agents/", ".codex/")) or (scope == "main" and name == "AGENTS.md")) and rules.get(name) != content:
                raise ValueError("Fixture must not override candidate rules")
    project = output / "project"
    project.mkdir(parents=True)
    for name, content in payload.items():
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    if scope == "main":
        spec = importlib.util.spec_from_file_location(
            "project_install", ROOT / "source/initializer/scripts/project_install.py")
        links = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(links)
        links.create_workflow_link(project / ".agents/sdd-workflow/sdd", (project / ".agents/sdd").resolve())
        links.create_workflow_link(project / ".agents/sdd-workflow/agents", (project / ".codex/agents").resolve())
    shared = ".agents/sdd"
    if selected_role is not None:
        shared = ".agents/sdd-workflow/sdd"
        (project / ".codex/config.toml").write_text(
            f'[agents]\nmax_threads = 1\nmax_depth = 1\n\n[agents.{selected_role}]\n'
            f'config_file = "agents/{selected_role}.toml"\n', encoding="utf-8")
    guidance = (f"# 隔离评测项目\n\n先读 README.md 和 docs/index.md。共享资源位于 `{shared}/`。"
                f"按需读[仓库治理]({shared}/references/sdd-repository-governance.md)和"
                f"[执行协作]({shared}/references/delegation.md)。")
    if selected_role is None:
        guidance += (f"实施按[实施交接]({shared}/references/delegation.md#实施交接)定位共享实施规则。"
                     "Skill 与角色以本目录候选快照为准。")
    if scope in ("project", "review-role"):
        (project / "AGENTS.md").write_text(guidance + "仅在本目录内执行当前任务。\n", encoding="utf-8")
    (project / "TASK.txt").write_text(case["input"] + "\n", encoding="utf-8")
    # List candidate files whose bytes were actually retained in the project.
    manifest = {
        "case": case["id"],
        "candidate_source": str(candidate.resolve()),
        "files": {
            name: hashlib.sha256(content).hexdigest()
            for name, content in sorted(rules.items())
            if (project / name).read_bytes() == content
        },
        "preparation_only": True,
        "model_execution": "UNVERIFIED",
    }
    if selected_role is not None:
        manifest["role"] = selected_role
    if scope == "main":
        manifest["links"] = {".agents/sdd-workflow/sdd": ".agents/sdd",
                             ".agents/sdd-workflow/agents": ".codex/agents"}
    if scope == "workflow-review":
        manifest["candidate_source"] = str(ROOT / REVIEW_SKILL)
    (output / "candidate-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "evaluation.json").write_text(json.dumps({
        "case": case["id"], "expected": case["expected"], "forbidden": case["forbidden"],
        "setup": case.get("evaluation_setup"),
        "model_execution": "UNVERIFIED",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return project


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", required=True, dest="case_ids")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = load_cases()
    if len(args.case_ids) != len(set(args.case_ids)):
        parser.error("Repeated --case")
    if args.output.exists() or args.output.is_symlink():
        parser.error(f"Output already exists: {args.output}")
    for name in args.case_ids:
        if name not in cases:
            parser.error(f"Unknown case: {name}")
    for name in args.case_ids:
        print(prepare_case(cases[name], args.output / name))


if __name__ == "__main__":
    main()
