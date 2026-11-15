"""Exercise uvx and project initialization using an isolated installation directory."""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib


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
        selector = ["--skills-dir", str(skills), "--agents-dir", str(agents)]
        inspected = subprocess.run([*cli, "inspect", *selector], check=True, capture_output=True, text=True, encoding="utf-8")
        assert "Status: not installed" in inspected.stdout
        assert str(agents / "review-prompt.toml") in inspected.stdout
        assert not skills.exists()
        assert not agents.exists()
        command = [*cli, "install", *selector]
        subprocess.run(command, check=True)
        role = agents / "review-prompt.toml"
        role_content = role.read_bytes()
        assert tomllib.loads(role_content.decode("utf-8"))["name"] == "review-prompt"
        subprocess.run(command, check=True)
        skill = skills / "sdd-init"
        assert role_content == role.read_bytes() == (skill / "assets/user-agents/review-prompt.toml").read_bytes()
        assert len(list(skills.rglob("SKILL.md"))) == 1
        project = root / "project"
        project.mkdir()
        initialize = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"), "--root", str(project), "init"]
        subprocess.run(initialize, check=True)
        workflow = project / ".agents/skills/sdd-workflow"
        self_shared = skills.with_name(f"{skills.name}-sdd-init-shared")
        assert workflow.samefile(self_shared)
        before = {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
        subprocess.run(command, check=True)
        assert before == {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
        assert {p.parent.name for p in (workflow / "skills").glob("*/SKILL.md")} == {
            "sdd-develop", "sdd-architecture", "sdd-bugfix", "sdd-test-loop", "sdd-refactor",
            "sdd-deliver",
        }
        assert not (workflow / "sdd/assets/prompt_review_template.md").exists()
        refactor = workflow / "skills/sdd-refactor/SKILL.md"
        assert "name: sdd-refactor\n" in refactor.read_text(encoding="utf-8")
        guidance = (project / "AGENTS.md").read_text(encoding="utf-8")
        assert f"[sdd-refactor]({refactor.relative_to(project).as_posix()})" in guidance
        assert "sdd-review-prompt" not in guidance and "review-repo-prompt" not in guidance
        config = project / ".codex/config.toml"
        roles = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]
        assert set(roles) == {
            "sdd-architect", "sdd-coder", "sdd-devops", "sdd-product-manager", "sdd-doc-consistency",
        }
        assert not (project / ".codex/agents").exists()
        for name, reference in roles.items():
            assert (config.parent / reference["config_file"]).samefile(self_shared / "agents" / f"{name}.toml")
        subprocess.run(initialize, check=True)
        assert before == {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
        inspection = subprocess.run([*initialize[:-1], "inspect"], check=True, capture_output=True, text=True, encoding="utf-8")
        assert "Project connection is current" in inspection.stdout
        recovered = subprocess.run([*cli, "recover", *selector], check=True, capture_output=True, text=True, encoding="utf-8")
        assert "No pending user-level recovery" in recovered.stdout
        assert "Status: current" in recovered.stdout
        assert settings.read_bytes() == b'model = "user-choice"\r\n'
    print("Package smoke test passed; temporary user and project directories removed.")


if __name__ == "__main__":
    main()
