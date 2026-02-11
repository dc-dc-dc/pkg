import os
import shutil
import stat
import subprocess
from pathlib import Path

from rich.console import Console

from .base import BuildTool
from ..runner import run_command

console = Console()

BIN_DIR = Path.home() / "bin"


class BashTool(BuildTool):
    @property
    def name(self) -> str:
        return "bash"

    def init(self, name: str | None = None, git: bool = True) -> int:
        src_dir = self.project_dir / "src"
        src_dir.mkdir(exist_ok=True)

        test_dir = self.project_dir / "tests"
        test_dir.mkdir(exist_ok=True)

        # Create example script
        hello_script = src_dir / "hello.sh"
        hello_script.write_text(
            "#!/usr/bin/env bash\nset -euo pipefail\n\necho 'Hello, World!'\n"
        )
        hello_script.chmod(hello_script.stat().st_mode | stat.S_IEXEC)

        # Create example test
        hello_test = test_dir / "hello_test.sh"
        hello_test.write_text(
            '#!/usr/bin/env bash\nset -euo pipefail\n\n'
            'output=$(bash "$(dirname "$0")/../src/hello.sh")\n\n'
            'if [ "$output" != "Hello, World!" ]; then\n'
            '  echo "FAIL: expected \'Hello, World!\' but got \'$output\'"\n'
            '  exit 1\n'
            'fi\n\n'
            'echo "PASS: hello"\n'
        )
        hello_test.chmod(hello_test.stat().st_mode | stat.S_IEXEC)

        self._create_gitignore()
        return 0

    def build(self) -> int:
        test_result = self.test()
        if test_result != 0:
            console.print("[red]Build aborted: tests failed[/red]")
            return test_result

        src_dir = self.project_dir / "src"
        if not src_dir.exists():
            console.print("[red]No src directory found[/red]")
            return 1

        scripts = list(src_dir.glob("*.sh"))
        if not scripts:
            console.print("[dim]No scripts to install[/dim]")
            return 0

        BIN_DIR.mkdir(parents=True, exist_ok=True)

        installed = []
        for script in scripts:
            dest = BIN_DIR / script.name
            shutil.copy2(script, dest)
            dest.chmod(dest.stat().st_mode | stat.S_IEXEC)
            installed.append(script.name)

        console.print(
            f"[green]Installed to ~/bin: {', '.join(installed)}[/green]"
        )
        return 0

    def test(self) -> int:
        test_dir = self.project_dir / "tests"
        if not test_dir.exists():
            console.print("[dim]No tests directory found[/dim]")
            return 0

        test_files = sorted(test_dir.glob("*_test.sh"))
        if not test_files:
            console.print("[dim]No test files found[/dim]")
            return 0

        failed = []
        passed = []
        for test_file in test_files:
            console.print(f"[blue]> bash {test_file.name}[/blue]")
            result = subprocess.run(
                ["bash", str(test_file)],
                cwd=self.project_dir,
            )
            if result.returncode != 0:
                failed.append(test_file.name)
            else:
                passed.append(test_file.name)

        if passed:
            console.print(f"[green]{len(passed)} passed[/green]")
        if failed:
            console.print(
                f"[red]{len(failed)} failed: {', '.join(failed)}[/red]"
            )
            return 1

        return 0

    def install(self) -> int:
        # Bash projects have no dependencies to install
        console.print("[dim]No dependencies to install for bash projects[/dim]")
        return 0

    def run(self, script: str, args: list[str] | None = None) -> int:
        script_path = self.project_dir / "src" / script
        if not script_path.exists():
            console.print(f"[red]Script not found: {script}[/red]")
            return 1
        cmd = ["bash", str(script_path)]
        if args:
            cmd.extend(args)
        return run_command(cmd, cwd=self.project_dir)

    def clean(self) -> int:
        src_dir = self.project_dir / "src"
        if not src_dir.exists():
            console.print("[dim]Nothing to clean[/dim]")
            return 0

        scripts = list(src_dir.glob("*.sh"))
        removed = []
        for script in scripts:
            installed = BIN_DIR / script.name
            if installed.exists():
                installed.unlink()
                removed.append(script.name)

        if removed:
            console.print(
                f"[green]Removed from ~/bin: {', '.join(removed)}[/green]"
            )
        else:
            console.print("[dim]Nothing to clean[/dim]")

        return 0

    def uplift(self) -> int:
        src_dir = self.project_dir / "src"
        src_dir.mkdir(exist_ok=True)

        test_dir = self.project_dir / "tests"
        test_dir.mkdir(exist_ok=True)

        self._create_gitignore()
        return 0

    def _create_gitignore(self) -> None:
        gitignore_content = """*.log
.env
.env.*
.DS_Store
"""
        gitignore_path = self.project_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text(gitignore_content)
            console.print("[green]Created .gitignore[/green]")
