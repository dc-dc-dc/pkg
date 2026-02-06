from pathlib import Path

from rich.console import Console

from .config import CONFIG_FILENAME

console = Console()

DEFAULT_CONFIG = '''[pkg]
tool = "uv"

[hooks.build]
pre = []
post = []

[hooks.test]
pre = []
post = []

[hooks.install]
pre = []
post = []

[plugins]
enabled = []
'''


def create_pkg_config(project_dir: Path, tool: str = "uv") -> None:
    config_path = project_dir / CONFIG_FILENAME
    if config_path.exists():
        console.print(f"[yellow]{CONFIG_FILENAME} already exists[/yellow]")
        return

    content = DEFAULT_CONFIG.replace('tool = "uv"', f'tool = "{tool}"')
    config_path.write_text(content)
    console.print(f"[green]Created {CONFIG_FILENAME}[/green]")
