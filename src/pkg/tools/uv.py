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
    ".coverage",
    "htmlcov",
    "build",
]


class UvTool(BuildTool):
    @property
    def name(self) -> str:
        return "uv"

    def init(self, name: str | None = None, git: bool = True) -> int:
        code = run_command(["uv", "init"], cwd=self.project_dir)
        if code != 0:
            return code

        self._add_dev_dependencies()
        self._create_gitignore()
        return 0

    def build(self) -> int:
        code = run_command(["uv", "build"], cwd=self.project_dir)
        if code != 0:
            return code
        return self.test()

    def test(self) -> int:
        return run_command(["uv", "run", "pytest"], cwd=self.project_dir)

    def install(self) -> int:
        return run_command(["uv", "sync", "--group", "dev"], cwd=self.project_dir)

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

    def uplift(self) -> int:
        self._add_dev_dependencies()
        self._create_gitignore()
        return 0

    def _remove_path(self, path: Path) -> None:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def _add_dev_dependencies(self) -> None:
        pyproject_path = self.project_dir / "pyproject.toml"
        if not pyproject_path.exists():
            return

        content = pyproject_path.read_text()
        if "[dependency-groups]" in content:
            return

        dev_config = """
[dependency-groups]
dev = ["pytest>=8.0.0", "pytest-mock>=3.12.0", "pytest-cov>=4.1.0"]

[tool.pytest.ini_options]
addopts = "--cov=. --cov-report=term-missing --cov-report=html --cov-fail-under=90"
"""
        content += dev_config
        pyproject_path.write_text(content)
        console.print("[green]Added dev dependencies and pytest config[/green]")

    def _create_gitignore(self) -> None:
        gitignore_content = """.venv/
dist/
*.egg-info/
__pycache__/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
htmlcov/
build/

*.pyc
.env
.env.*
"""
        gitignore_path = self.project_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text(gitignore_content)
            console.print("[green]Created .gitignore[/green]")
