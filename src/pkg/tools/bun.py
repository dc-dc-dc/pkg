import re
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
        test_cfg = self.config.test if self.config else None
        exclude = test_cfg.exclude if test_cfg else []
        skip = test_cfg.skip if test_cfg else None

        cmd = ["bun", "test", "--coverage"]

        if exclude:
            patterns = ["**/*.test.ts", "**/*.test.tsx", "**/*.test.js", "**/*.test.jsx",
                        "**/*.spec.ts", "**/*.spec.tsx", "**/*.spec.js", "**/*.spec.jsx"]
            test_files = []
            for pattern in patterns:
                for path in self.project_dir.glob(pattern):
                    if "node_modules" not in path.parts:
                        test_files.append(path)

            filtered = [
                str(p.relative_to(self.project_dir))
                for p in test_files
                if not any(re.search(excl, str(p)) for excl in exclude)
            ]
            if not filtered:
                console.print("[yellow]No test files to run after exclusions[/yellow]")
                return 0
            cmd += filtered

        if skip:
            console.print("[yellow]test.skip is not supported by bun — use test.exclude for file exclusions[/yellow]")

        return run_command(cmd, cwd=self.project_dir)

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

        changed = False

        if "devDependencies" not in data:
            data["devDependencies"] = {}

        if "@types/bun" not in data["devDependencies"]:
            data["devDependencies"]["@types/bun"] = "latest"
            changed = True

        scripts = data.get("scripts", {})
        if "test" not in scripts or "build" not in scripts:
            scripts.setdefault("test", "bun test --coverage")
            scripts.setdefault("build", "bun build ./index.ts --outdir ./dist")
            data["scripts"] = scripts
            changed = True

        if changed:
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
