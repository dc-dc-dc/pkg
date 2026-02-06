import subprocess
from pathlib import Path

from rich.console import Console

console = Console()


def run_command(
    args: list[str],
    cwd: Path,
    capture_output: bool = False,
) -> int:
    console.print(f"[blue]> {' '.join(args)}[/blue]")
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=capture_output,
    )
    return result.returncode
