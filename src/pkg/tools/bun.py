import shutil
from pathlib import Path

from rich.console import Console

from .base import BuildTool
from ..runner import run_command

console = Console()

CLEAN_PATTERNS = [
    "node_modules",
    "dist",
    ".turbo",
    "coverage",
    ".next",
    ".nuxt",
    ".output",
    "build",
]


class BunTool(BuildTool):
    @property
    def name(self) -> str:
        return "bun"

    def init(self, name: str | None = None, git: bool = True) -> int:
        code = run_command(["bun", "init", "-y"], cwd=self.project_dir)
        if code != 0:
            return code

        self._add_dev_dependencies()
        self._create_gitignore()
        return 0

    def build(self) -> int:
        test_result = self.test()
        if test_result != 0:
            console.print("[red]Build aborted: tests failed[/red]")
            return test_result
        return run_command(["bun", "run", "build"], cwd=self.project_dir)

    def test(self) -> int:
        return run_command(["bun", "test", "--coverage"], cwd=self.project_dir)

    def install(self) -> int:
        return run_command(["bun", "install"], cwd=self.project_dir)

    def run(self, script: str, args: list[str] | None = None) -> int:
        cmd = ["bun", "run", script]
        if args:
            cmd.extend(args)
        return run_command(cmd, cwd=self.project_dir)

    def clean(self) -> int:
        cleaned = []
        for pattern in CLEAN_PATTERNS:
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
        package_json_path = self.project_dir / "package.json"
        if not package_json_path.exists():
            return

        import json
        data = json.loads(package_json_path.read_text())

        if "devDependencies" not in data:
            data["devDependencies"] = {}

        if "@types/bun" in data.get("devDependencies", {}):
            return

        data["devDependencies"]["@types/bun"] = "latest"
        data["scripts"] = data.get("scripts", {})
        data["scripts"]["test"] = "bun test --coverage"
        data["scripts"]["build"] = "bun build ./index.ts --outdir ./dist"

        package_json_path.write_text(json.dumps(data, indent=2) + "\n")
        console.print("[green]Added dev dependencies and scripts[/green]")

    def _create_gitignore(self) -> None:
        gitignore_content = """node_modules/
dist/
.turbo/
coverage/
.next/
.nuxt/
.output/
build/
*.log
.env
.env.*
.DS_Store
"""
        gitignore_path = self.project_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text(gitignore_content)
            console.print("[green]Created .gitignore[/green]")
