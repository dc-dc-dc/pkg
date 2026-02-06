import shutil
from pathlib import Path

from rich.console import Console

from .base import BuildTool
from ..runner import run_command

console = Console()

CLEAN_PATTERNS = [
    ".venv",
    "dist",
    "*.egg-info",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "build",
]


class UvTool(BuildTool):
    @property
    def name(self) -> str:
        return "uv"

    def init(self, git: bool = True) -> int:
        code = run_command(["uv", "init"], cwd=self.project_dir)
        if code != 0:
            return code

        if git and not (self.project_dir / ".git").exists():
            code = run_command(["git", "init"], cwd=self.project_dir)
            if code != 0:
                return code
            self._create_gitignore()

        return 0

    def build(self) -> int:
        return run_command(["uv", "build"], cwd=self.project_dir)

    def test(self) -> int:
        return run_command(["uv", "run", "pytest"], cwd=self.project_dir)

    def install(self) -> int:
        return run_command(["uv", "sync"], cwd=self.project_dir)

    def run(self, script: str, args: list[str] | None = None) -> int:
        cmd = ["uv", "run", script]
        if args:
            cmd.extend(args)
        return run_command(cmd, cwd=self.project_dir)

    def clean(self) -> int:
        cleaned = []
        for pattern in CLEAN_PATTERNS:
            if "*" in pattern:
                for path in self.project_dir.glob(pattern):
                    self._remove_path(path)
                    cleaned.append(str(path.relative_to(self.project_dir)))
            else:
                path = self.project_dir / pattern
                if path.exists():
                    self._remove_path(path)
                    cleaned.append(pattern)

        if cleaned:
            console.print(f"[green]Cleaned: {', '.join(cleaned)}[/green]")
        else:
            console.print("[dim]Nothing to clean[/dim]")

        return 0

    def _remove_path(self, path: Path) -> None:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def _create_gitignore(self) -> None:
        gitignore_content = """.venv/
dist/
*.egg-info/
__pycache__/
.pytest_cache/
.ruff_cache/
.mypy_cache/
build/
*.pyc
.env
.env.*
"""
        gitignore_path = self.project_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text(gitignore_content)
            console.print("[green]Created .gitignore[/green]")
