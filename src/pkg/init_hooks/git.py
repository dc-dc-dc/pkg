import subprocess
from pathlib import Path

from . import register


class GitHook:
    name = "git"
    enabled_by_default = True

    def run(self, project_dir: Path, name: str) -> int:
        """Initialize a git repository in the project directory."""
        if (project_dir / ".git").exists():
            return 0

        result = subprocess.run(
            ["git", "init"],
            cwd=project_dir,
            capture_output=True,
        )
        return result.returncode


register(GitHook())
