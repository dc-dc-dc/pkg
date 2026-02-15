import shutil
from pathlib import Path

from rich.console import Console

from .base import BuildTool
from ..runner import run_command

console = Console()

CLEAN_PATTERNS = [
    "build",
    "vendor",
    "coverage.out",
    "*.test",
]


class GoTool(BuildTool):
    @property
    def name(self) -> str:
        return "go"

    def init(self, name: str | None = None, git: bool = True) -> int:
        module = name or self.project_dir.name
        code = run_command(["go", "mod", "init", module], cwd=self.project_dir)
        if code != 0:
            return code

        self._create_dirs()
        self._create_main_go()
        self._create_gitignore()
        return 0

    def build(self) -> int:
        vet_result = run_command(["go", "vet", "./..."], cwd=self.project_dir)
        if vet_result != 0:
            console.print("[red]Build aborted: vet failed[/red]")
            return vet_result

        test_result = self.test()
        if test_result != 0:
            console.print("[red]Build aborted: tests failed[/red]")
            return test_result

        build_dir = self.project_dir / "build"
        build_dir.mkdir(exist_ok=True)

        output = build_dir / self.project_dir.name
        return run_command(
            ["go", "build", "-o", str(output), "./cmd/..."],
            cwd=self.project_dir,
        )

    def test(self) -> int:
        return run_command(["go", "test", "-cover", "./..."], cwd=self.project_dir)

    def install(self) -> int:
        return run_command(["go", "mod", "tidy"], cwd=self.project_dir)

    def run(self, script: str, args: list[str] | None = None) -> int:
        cmd = ["go", "run", script]
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
        self._create_dirs()
        self._create_gitignore()
        return 0

    def _remove_path(self, path: Path) -> None:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def _create_dirs(self) -> None:
        for dirname in ["cmd", "pkg", "internal", "scripts"]:
            d = self.project_dir / dirname
            d.mkdir(exist_ok=True)
        console.print("[green]Created cmd/, pkg/, internal/, scripts/[/green]")

    def _create_main_go(self) -> None:
        main_go = self.project_dir / "cmd" / "main.go"
        if main_go.exists():
            return

        main_go.write_text("""package main

import "fmt"

func main() {
\tfmt.Println("Hello, World!")
}
""")
        console.print("[green]Created cmd/main.go[/green]")

    def _create_gitignore(self) -> None:
        gitignore_content = """build/
vendor/
coverage.out
*.test
*.exe
*.exe~
*.dll
*.so
*.dylib
.env
.env.*
.DS_Store
"""
        gitignore_path = self.project_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text(gitignore_content)
            console.print("[green]Created .gitignore[/green]")
