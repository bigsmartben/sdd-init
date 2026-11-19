"""Exercise uvx and project initialization using an isolated installation directory."""
import argparse
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import tomllib


def local_files(root):
    files, pending = {}, [root]
    while pending:
        for path in pending.pop().iterdir():
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                continue
            if path.is_dir():
                pending.append(path)
            elif path.is_file():
                files[path.relative_to(root)] = path.read_bytes()
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="source", required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="sdd-package-") as temporary:
        root = Path(temporary)
        skills = root / "skills"
        config = root / "codex"
        config.mkdir()
        settings = config / "config.toml"
        settings.write_bytes(b'model = "user-choice"\r\n')
        agents = config / "agents"
        cli = ["uvx", "--from", args.source, "sdd-init"]
        selector = ["--skills-dir", str(skills)]
        inspected = subprocess.run([*cli, "inspect", *selector], check=True, capture_output=True, text=True, encoding="utf-8")
        assert "Status: not installed" in inspected.stdout
        assert "User role:" not in inspected.stdout
        assert not skills.exists()
        assert not agents.exists()
        command = [*cli, "install", *selector]
        subprocess.run(command, check=True)
        assert not agents.exists()
        subprocess.run(command, check=True)
        skill = skills / "sdd-init"
        assert not (skill / "assets/user-agents/review-prompt.toml").exists()
        assert len(list(skills.rglob("SKILL.md"))) == 1
        project = root / "project"
        project.mkdir()
        initialize = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"), "--root", str(project), "--harness", "both", "init"]
        subprocess.run(initialize, check=True)
        workflow = project / ".agents/sdd-workflow"
        self_shared = skills.with_name(f"{skills.name}-sdd-init-shared")
        assert workflow.samefile(self_shared)
        before = local_files(project)
        subprocess.run(command, check=True)
        assert before == local_files(project)
        project_skills = project / ".agents/skills"
        assert {p.name for p in project_skills.iterdir()} == {
            "sdd-develop", "sdd-architecture", "sdd-bugfix", "sdd-test-loop", "sdd-refactor",
            "sdd-deliver",
        }
        for path in project_skills.iterdir():
            info = path.lstat()
            assert stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", None) == 0xA0000003
            assert (path / "SKILL.md").samefile(self_shared / "skills" / path.name / "SKILL.md")
        assert not (workflow / "sdd/assets/prompt_review_template.md").exists()
        refactor = project_skills / "sdd-refactor/SKILL.md"
        assert "name: sdd-refactor\n" in refactor.read_text(encoding="utf-8")
        guidance = (project / "AGENTS.md").read_text(encoding="utf-8")
        assert f"[sdd-refactor]({refactor.relative_to(project).as_posix()})" in guidance
        assert "sdd-review-prompt" not in guidance and "review-repo-prompt" not in guidance
        config = project / ".codex/config.toml"
        roles = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]
        assert set(roles) == {
            "sdd-architect", "sdd-coder", "sdd-devops", "sdd-product-manager", "sdd-doc-consistency",
            "review-prompt",
        }
        assert not (project / ".codex/agents").exists()
        for name, reference in roles.items():
            assert (config.parent / reference["config_file"]).samefile(
                self_shared / "roles/codex" / f"{name}.toml")
            copilot = project / ".github/agents" / f"{name}.agent.md"
            assert copilot.is_file()
            adapter = copilot.read_text(encoding="utf-8")
            assert "model:" not in adapter
            assert "target:" not in adapter.split("---", 2)[1]
            assert f".github/sdd-workflow/roles/shared/{name}.md" in adapter
        assert (project / ".github/sdd-workflow").samefile(self_shared)
        subprocess.run(initialize, check=True)
        assert before == local_files(project)
        inspection = subprocess.run([*initialize[:-1], "inspect"], check=True, capture_output=True, text=True, encoding="utf-8")
        assert "Project connection is current" in inspection.stdout
        for harness in ("codex", "copilot"):
            assert f"Installed roles ({harness}): {', '.join(sorted(roles))}" in inspection.stdout
        recovered = subprocess.run([*cli, "recover", *selector], check=True, capture_output=True, text=True, encoding="utf-8")
        assert "No pending user-level recovery" in recovered.stdout
        assert "Status: current" in recovered.stdout
        assert settings.read_bytes() == b'model = "user-choice"\r\n'
    print("Package smoke test passed; temporary user and project directories removed.")


if __name__ == "__main__":
    main()
