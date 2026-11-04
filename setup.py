"""Build the canonical skill resources into the wheel, never into user directories."""
import runpy
import tempfile
from pathlib import Path
import shutil

from setuptools import setup
from setuptools.command.build_py import build_py


class BuildWithResources(build_py):
    def run(self):
        super().run()
        builder = runpy.run_path(str(Path(__file__).parent / "scripts/build_release.py"))
        with tempfile.TemporaryDirectory() as temporary:
            skill = builder["build"](Path(temporary) / "skill")
            destination = Path(self.build_lib) / "sdd_init/resources"
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(skill, destination)


setup(cmdclass={"build_py": BuildWithResources})
