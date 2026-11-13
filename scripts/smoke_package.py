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
        command = ["uvx", "--from", args.source, "sdd-init", "install", "--skills-dir", str(skills)]
        subprocess.run(command, check=True)
        subprocess.run(command, check=True)
        skill = skills / "sdd-init"
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
            "sdd-doc", "sdd-imp", "sdd-test-loop", "sdd-review-code",
            "sdd-review-prompt", "sdd-commit", "sdd-deploy",
        }
        config = project / ".codex/config.toml"
        roles = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]
        assert len(roles) == 5 and not (project / ".codex/agents").exists()
        for name, reference in roles.items():
            assert (config.parent / reference["config_file"]).samefile(self_shared / "agents" / f"{name}.toml")
        subprocess.run(initialize, check=True)
        assert before == {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
    print("Package smoke test passed; temporary user and project directories removed.")


if __name__ == "__main__":
    main()
